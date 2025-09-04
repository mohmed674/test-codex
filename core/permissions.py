# core/permissions.py
from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View


class IsCoreManager(BasePermission):
    """
    يسمح فقط لمدراء النواة الأساسية بالوصول.
    """

    def has_permission(self, request: Request, view: View) -> bool:
        user: Any = getattr(request, "user", None)
        return bool(
            user
            and getattr(user, "is_authenticated", False)
            and user.groups.filter(name="Core Managers").exists()
        )
