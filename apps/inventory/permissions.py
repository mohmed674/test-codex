# ERP_CORE/inventory/permissions.py
from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

# ============================ Lazy models (runtime-safe) ============================

InventoryItem = apps.get_model("inventory", "InventoryItem")
InventoryMovement = apps.get_model("inventory", "InventoryMovement")
Warehouse = apps.get_model("inventory", "Warehouse")

# Ensure model_name strings are available even if models are None
ITEM_MODEL_NAME = str(
    getattr(getattr(InventoryItem, "_meta", None), "model_name", "inventoryitem")
)
MOVE_MODEL_NAME = str(
    getattr(
        getattr(InventoryMovement, "_meta", None), "model_name", "inventorymovement"
    )
)
WH_MODEL_NAME = str(
    getattr(getattr(Warehouse, "_meta", None), "model_name", "warehouse")
)

# ============================ Roles / Groups ============================

ROLE_INVENTORY_MANAGER = "Inventory Manager"
ROLE_STORE_KEEPER = "Store Keeper"
ROLE_INVENTORY_AUDITOR = "Inventory Auditor"
ROLE_INVENTORY_VIEWER = "Inventory Viewer"

ALL_ROLES: tuple[str, ...] = (
    ROLE_INVENTORY_MANAGER,
    ROLE_STORE_KEEPER,
    ROLE_INVENTORY_AUDITOR,
    ROLE_INVENTORY_VIEWER,
)

# خرائط أدوار -> صلاحيات نمطية على الموديلات (Django add/change/delete/view)
DEFAULT_ROLE_PERMS: dict[str, Mapping[str, Sequence[str]]] = {
    ROLE_INVENTORY_MANAGER: {
        ITEM_MODEL_NAME: ("add", "change", "delete", "view"),
        MOVE_MODEL_NAME: ("add", "change", "delete", "view"),
        WH_MODEL_NAME: ("add", "change", "delete", "view"),
    },
    ROLE_STORE_KEEPER: {
        ITEM_MODEL_NAME: ("change", "view"),
        MOVE_MODEL_NAME: ("add", "change", "view"),
        WH_MODEL_NAME: ("view",),
    },
    ROLE_INVENTORY_AUDITOR: {
        ITEM_MODEL_NAME: ("view",),
        MOVE_MODEL_NAME: ("view",),
        WH_MODEL_NAME: ("view",),
    },
    ROLE_INVENTORY_VIEWER: {
        ITEM_MODEL_NAME: ("view",),
        MOVE_MODEL_NAME: ("view",),
        WH_MODEL_NAME: ("view",),
    },
}

# ============================ Helpers ============================


def _perm_codename(action: str, model_lower: str) -> str:
    return f"{action}_{model_lower}"


def _assign_perms_to_group(
    group: Group, model_lower: str, actions: Iterable[str]
) -> None:
    for action in actions:
        try:
            perm = Permission.objects.get(codename=_perm_codename(action, model_lower))
            group.permissions.add(perm)
        except Permission.DoesNotExist:
            # قد لا تكون الصلاحية متاحة قبل الهجرات—تجاهل بصمت
            continue


def ensure_default_groups() -> None:
    """
    إنشاء مجموعات الصلاحيات الافتراضية وتوزيع الصلاحيات عليها (idempotent).
    يمكن استدعاؤها من ready() أو أمر إدارة.
    """
    for role, mapping in DEFAULT_ROLE_PERMS.items():
        group, _ = Group.objects.get_or_create(name=role)
        for model_lower, actions in mapping.items():
            _assign_perms_to_group(group, model_lower, actions)


def user_in_roles(user: Any, roles: Iterable[str]) -> bool:
    """فحص الانتماء للأدوار مع تحمل اختلافات نماذج المستخدم."""
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    role_set = set(roles)
    groups = getattr(user, "groups", None)
    if groups is not None and hasattr(groups, "filter"):
        return groups.filter(name__in=role_set).exists()
    return False


def assign_user_role(user: Any, role: str) -> None:
    """إلحاق المستخدم بمجموعة الدور المطلوبة (ينشئ الدور إن لم يكن موجودًا)."""
    group, _ = Group.objects.get_or_create(name=role)
    groups = getattr(user, "groups", None)
    if groups is not None and hasattr(groups, "add"):
        groups.add(group)


# ============================ Decorators / Mixins ============================


def require_roles(*roles: str):
    """
    Decorator لفرض دور/أدوار على view function.
    """

    def decorator(view_func):
        def _wrapped(request: HttpRequest, *args, **kwargs):
            if not request.user.is_authenticated or not user_in_roles(
                request.user, roles
            ):
                raise PermissionDenied(_("ليست لديك صلاحية الوصول لهذه الصفحة."))
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class RoleRequiredMixin:
    """
    للاستخدام مع CBVs:
        class MyView(RoleRequiredMixin, View):
            required_roles = (ROLE_INVENTORY_MANAGER,)
    """

    required_roles: tuple[str, ...] = ()

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if self.required_roles and not user_in_roles(request.user, self.required_roles):
            raise PermissionDenied(_("ليست لديك صلاحية الوصول لهذه الصفحة."))
        return super().dispatch(request, *args, **kwargs)  # type: ignore[misc]


# ============================ Object Level Checks ============================


def _has_model_perm(user: Any, action: str, model_lower: str) -> bool:
    return hasattr(user, "has_perm") and user.has_perm(
        _perm_codename(action, model_lower)
    )


def can_view_item(user: Any, item: Any) -> bool:
    if getattr(user, "is_superuser", False):
        return True
    if _has_model_perm(user, "view", ITEM_MODEL_NAME):
        return True
    # قد يسمح المخزن المرتبط بالعنصر بدور المشاهدة للمخزن فقط
    return user_in_roles(
        user,
        (
            ROLE_INVENTORY_MANAGER,
            ROLE_INVENTORY_AUDITOR,
            ROLE_INVENTORY_VIEWER,
            ROLE_STORE_KEEPER,
        ),
    )


def can_edit_item(user: Any, item: Any) -> bool:
    if getattr(user, "is_superuser", False):
        return True
    if _has_model_perm(user, "change", ITEM_MODEL_NAME):
        return True
    return user_in_roles(user, (ROLE_INVENTORY_MANAGER, ROLE_STORE_KEEPER))


def can_delete_item(user: Any, item: Any) -> bool:
    if getattr(user, "is_superuser", False):
        return True
    if _has_model_perm(user, "delete", ITEM_MODEL_NAME):
        return True
    return user_in_roles(user, (ROLE_INVENTORY_MANAGER,))


def can_create_movement(user: Any) -> bool:
    if getattr(user, "is_superuser", False):
        return True
    if _has_model_perm(user, "add", MOVE_MODEL_NAME):
        return True
    return user_in_roles(user, (ROLE_INVENTORY_MANAGER, ROLE_STORE_KEEPER))


def can_adjust_stock(user: Any) -> bool:
    """اعتبر تعديل المخزون ضمن change على الحركة/العنصر + أدوار محددة."""
    if getattr(user, "is_superuser", False):
        return True
    return (
        _has_model_perm(user, "change", MOVE_MODEL_NAME)
        or _has_model_perm(user, "change", ITEM_MODEL_NAME)
        or user_in_roles(user, (ROLE_INVENTORY_MANAGER, ROLE_STORE_KEEPER))
    )


# ============================ DRF Integration (اختياري) ============================

try:
    from rest_framework.permissions import BasePermission  # type: ignore

    class DRFInventoryPermission(BasePermission):
        """
        صلاحيات DRF عامة للعناصر والحركات:
        - SAFE methods: view
        - write methods: add/change/delete وفق الأدوار
        """

        def has_object_permission(self, request, view, obj) -> bool:
            user: Any = request.user  # type: ignore[assignment]
            method = request.method.upper()
            if method in ("GET", "HEAD", "OPTIONS"):
                return (
                    can_view_item(user, obj) if obj.__class__ == InventoryItem else True
                )
            if method in ("POST",):
                return (
                    can_create_movement(user)
                    if obj.__class__ == InventoryMovement
                    else can_edit_item(user, obj)
                )
            if method in ("PUT", "PATCH"):
                return can_edit_item(user, obj)
            if method == "DELETE":
                return can_delete_item(user, obj)
            return False

        def has_permission(self, request, view) -> bool:
            user: Any = request.user  # type: ignore[assignment]
            method = request.method.upper()
            if method in ("GET", "HEAD", "OPTIONS"):
                return _has_model_perm(user, "view", ITEM_MODEL_NAME) or user_in_roles(
                    user,
                    (
                        ROLE_INVENTORY_MANAGER,
                        ROLE_INVENTORY_AUDITOR,
                        ROLE_INVENTORY_VIEWER,
                        ROLE_STORE_KEEPER,
                    ),
                )
            if method == "POST":
                return can_create_movement(user)
            if method in ("PUT", "PATCH"):
                return _has_model_perm(
                    user, "change", ITEM_MODEL_NAME
                ) or user_in_roles(user, (ROLE_INVENTORY_MANAGER, ROLE_STORE_KEEPER))
            if method == "DELETE":
                return _has_model_perm(
                    user, "delete", ITEM_MODEL_NAME
                ) or user_in_roles(user, (ROLE_INVENTORY_MANAGER,))
            return False

except Exception:  # pragma: no cover
    DRFInventoryPermission = None  # type: ignore


# ============================ Bootstrap Utility ============================


def setup_permissions() -> None:
    """نقطة دخول لضبط المجموعات والصلاحيات الافتراضية."""
    ensure_default_groups()


__all__ = [
    # Roles
    "ROLE_INVENTORY_MANAGER",
    "ROLE_STORE_KEEPER",
    "ROLE_INVENTORY_AUDITOR",
    "ROLE_INVENTORY_VIEWER",
    "ALL_ROLES",
    # Helpers
    "ensure_default_groups",
    "setup_permissions",
    "user_in_roles",
    "assign_user_role",
    # Decorators / Mixins
    "require_roles",
    "RoleRequiredMixin",
    # Object-level checks
    "can_view_item",
    "can_edit_item",
    "can_delete_item",
    "can_create_movement",
    "can_adjust_stock",
    # DRF
    "DRFInventoryPermission",
]
