# ERP_CORE/pattern/permissions.py
from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest


def is_pattern_manager(user: Any) -> bool:
    """
    Return True if the user has the role/permission to manage patterns.
    Checks superuser/staff flags or custom perms.
    """
    if not user or isinstance(user, AnonymousUser):
        return False
    return bool(
        getattr(user, "is_superuser", False)
        or getattr(user, "is_staff", False)
        or user.has_perm("pattern.manage_patterns")
    )


def can_edit_pattern(user: Any, request: HttpRequest | None = None) -> bool:
    """
    Return True if the user is allowed to edit patterns.
    This uses `is_pattern_manager` and also checks a custom perm if defined.
    """
    if not user or isinstance(user, AnonymousUser):
        return False
    if is_pattern_manager(user):
        return True
    return user.has_perm("pattern.change_patterndesign")


def can_view_pattern(user: Any, request: HttpRequest | None = None) -> bool:
    """
    Return True if the user can at least view patterns.
    Staff or anyone with `view_patterndesign` is accepted.
    """
    if not user or isinstance(user, AnonymousUser):
        return False
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return True
    return user.has_perm("pattern.view_patterndesign")
