# ERP_CORE/departments/permissions.py

from rest_framework import permissions

class IsHROrReadOnly(permissions.BasePermission):
    """
    يسمح فقط لفريق الموارد البشرية بالتعديل، والبقية يمكنهم العرض فقط.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name='HR').exists()
