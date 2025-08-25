# ERP_CORE/core/permissions.py

from rest_framework import permissions

class IsCoreManager(permissions.BasePermission):
    """
    يسمح فقط لمدراء النواة الأساسية بالوصول.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Core Managers').exists()
