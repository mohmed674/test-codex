# ERP_CORE/discipline/permissions.py

from rest_framework import permissions

class IsHRorManager(permissions.BasePermission):
    """
    السماح فقط للمستخدمين من قسم الموارد البشرية أو المديرين بالوصول الكامل،
    بينما يُسمح للمشرفين بالقراءة فقط.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.groups.filter(name__in=['HR', 'مدير عام']).exists():
            return True

        if view.action in ['list', 'retrieve']:
            return user.groups.filter(name__in=['مشرف', 'رئيس قسم']).exists()

        return False
