# ERP_CORE/internal_monitoring/permissions.py
from __future__ import annotations

from typing import Any, Iterable, Sequence

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import ReportLog, RiskIncident

User = get_user_model()

# ============================ Roles / Groups ============================

ROLE_RISK_MANAGER = "Risk Manager"
ROLE_AUDITOR = "Auditor"
ROLE_SECURITY_OFFICER = "Security Officer"
ROLE_SUPERVISOR = "Supervisor"
ROLE_STAFF = "Staff"

ALL_ROLES: tuple[str, ...] = (
    ROLE_RISK_MANAGER,
    ROLE_SECURITY_OFFICER,
    ROLE_AUDITOR,
    ROLE_SUPERVISOR,
    ROLE_STAFF,
)

# خرائط أدوار -> صلاحيات نمطية على الموديلات
DEFAULT_ROLE_PERMS: dict[str, dict[str, Sequence[str]]] = {
    ROLE_RISK_MANAGER: {
        "riskincident": ("add", "change", "delete", "view"),
        "reportlog": ("add", "change", "delete", "view"),
    },
    ROLE_SECURITY_OFFICER: {
        "riskincident": ("add", "change", "view"),
        "reportlog": ("add", "view"),
    },
    ROLE_AUDITOR: {
        "riskincident": ("view",),
        "reportlog": ("view",),
    },
    ROLE_SUPERVISOR: {
        "riskincident": ("add", "view"),
        "reportlog": ("add", "view"),
    },
    ROLE_STAFF: {
        "riskincident": ("add", "view"),
        "reportlog": ("view",),
    },
}


# ============================ Helpers ============================


def _perm_codename(action: str, model_lower: str) -> str:
    return f"{action}_{model_lower}"


def _assign_perms_to_group(
    group: Group, model_lower: str, actions: Iterable[str]
) -> None:
    for action in actions:
        codename = _perm_codename(action, model_lower)
        try:
            perm = Permission.objects.get(codename=codename)
            group.permissions.add(perm)
        except Permission.DoesNotExist:
            continue


def ensure_default_groups() -> None:
    """
    إنشاء المجموعات الافتراضية وتوزيع صلاحيات قياسية عليها (idempotent).
    يستدعى عادة من signal ready() أو إدارة النظام.
    """
    risk_model: str = str(RiskIncident._meta.model_name)  # type: ignore[attr-defined]
    log_model: str = str(ReportLog._meta.model_name)  # type: ignore[attr-defined]

    for role, model_map in DEFAULT_ROLE_PERMS.items():
        group, _ = Group.objects.get_or_create(name=role)
        for model_lower, actions in model_map.items():
            if model_lower == "riskincident":
                target: str = risk_model
            elif model_lower == "reportlog":
                target = log_model
            else:
                target = model_lower
            _assign_perms_to_group(group, target, actions)


def user_in_roles(user: Any, roles: Iterable[str]) -> bool:
    """فحص الانتماء للأدوار مع تحمل اختلافات نماذج المستخدم."""
    if not user or not getattr(user, "is_authenticated", False):
        return False
    role_set = set(roles)
    groups = getattr(user, "groups", None)
    if groups is not None and hasattr(groups, "filter"):
        if groups.filter(name__in=role_set).exists():
            return True
    return bool(getattr(user, "is_superuser", False))


def assign_user_role(user: Any, role: str) -> None:
    """إلحاق المستخدم بمجموعة الدور المطلوبة (ينشئ الدور إن لم يكن موجودًا)."""
    group, _ = Group.objects.get_or_create(name=role)
    groups = getattr(user, "groups", None)
    if groups is not None and hasattr(groups, "add"):
        groups.add(group)


# ============================ Decorators / Mixins ============================


def require_roles(*roles: str):
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
    required_roles: tuple[str, ...] = ()

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if self.required_roles and not user_in_roles(request.user, self.required_roles):
            raise PermissionDenied(_("ليست لديك صلاحية الوصول لهذه الصفحة."))
        return super().dispatch(request, *args, **kwargs)  # type: ignore[misc]


# ============================ Object Level Checks ============================


def can_view_incident(user: Any, incident: RiskIncident) -> bool:
    if getattr(user, "is_superuser", False):
        return True
    if hasattr(user, "has_perm") and user.has_perm(_perm_codename("view", str(RiskIncident._meta.model_name))):  # type: ignore[attr-defined]
        return True
    if getattr(incident, "user_id", None) and getattr(incident, "user_id") == getattr(
        user, "id", None
    ):
        return True
    return user_in_roles(user, (ROLE_RISK_MANAGER, ROLE_SECURITY_OFFICER, ROLE_AUDITOR))


def can_edit_incident(user: Any, incident: RiskIncident) -> bool:
    if getattr(user, "is_superuser", False):
        return True
    if hasattr(user, "has_perm") and user.has_perm(_perm_codename("change", str(RiskIncident._meta.model_name))):  # type: ignore[attr-defined]
        return True
    if (
        getattr(incident, "user_id", None) == getattr(user, "id", None)
        and getattr(incident, "risk_level", "") != "HIGH"
    ):
        return True
    return user_in_roles(user, (ROLE_RISK_MANAGER, ROLE_SECURITY_OFFICER))


def can_resolve_incident(user: Any, incident: RiskIncident) -> bool:
    if not can_edit_incident(user, incident):
        return False
    return user_in_roles(user, (ROLE_RISK_MANAGER, ROLE_SECURITY_OFFICER))


# ============================ DRF Integration (اختياري) ============================

try:
    from rest_framework.permissions import BasePermission  # type: ignore

    class DRFRiskPermission(BasePermission):
        """
        صلاحيات DRF على مستوى الـ object:
        - SAFE methods: view permission
        - write methods: change permission + دور مناسب
        """

        def has_object_permission(self, request, view, obj) -> bool:
            user: Any = request.user  # type: ignore[assignment]
            if request.method in ("GET", "HEAD", "OPTIONS"):
                return can_view_incident(user, obj)
            return can_edit_incident(user, obj)

        def has_permission(self, request, view) -> bool:
            user: Any = request.user  # type: ignore[assignment]
            model_name = str(RiskIncident._meta.model_name)  # type: ignore[attr-defined]
            if request.method in ("GET", "HEAD", "OPTIONS"):
                return hasattr(user, "has_perm") and user.has_perm(  # type: ignore[attr-defined]
                    _perm_codename("view", model_name)
                )
            return hasattr(user, "has_perm") and user.has_perm(  # type: ignore[attr-defined]
                _perm_codename("add", model_name)
            )

except Exception:  # pragma: no cover
    DRFRiskPermission = None  # type: ignore


# ============================ Bootstrap Utility ============================


def setup_permissions() -> None:
    """نقطة دخول ملائمة لضبط المجموعات والصلاحيات الافتراضية."""
    ensure_default_groups()


__all__ = [
    # Roles
    "ROLE_RISK_MANAGER",
    "ROLE_AUDITOR",
    "ROLE_SECURITY_OFFICER",
    "ROLE_SUPERVISOR",
    "ROLE_STAFF",
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
    "can_view_incident",
    "can_edit_incident",
    "can_resolve_incident",
    # DRF
    "DRFRiskPermission",
]
