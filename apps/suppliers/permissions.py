# ERP_CORE/suppliers/permissions.py

from rest_framework import permissions

class IsManagerOrReadOnly(permissions.BasePermission):
    """
    صلاحيات: المدير فقط يستطيع تعديل الموردين، البقية عرض فقط.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name__in=['مدير', 'محاسب رئيسي']).exists()
