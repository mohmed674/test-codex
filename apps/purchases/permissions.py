# ERP_CORE/purchases/permissions.py

from rest_framework import permissions

class IsPurchaseManagerOrReadOnly(permissions.BasePermission):
    """
    يسمح فقط لمدير المشتريات أو للقراءة فقط
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name='Purchase Managers').exists()


class IsDepartmentOwner(permissions.BasePermission):
    """
    يسمح فقط للموظف بطلب شراء لقسمه
    """
    def has_object_permission(self, request, view, obj):
        return obj.department == request.user.employee.department
