# ERP_CORE/clients/permissions.py

from rest_framework import permissions

class IsClientManagerOrReadOnly(permissions.BasePermission):
    """
    يسمح فقط لمديري العملاء بالتعديل، والبقية يمكنهم العرض فقط.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name__in=['Client Managers', 'Sales Admins']).exists()
