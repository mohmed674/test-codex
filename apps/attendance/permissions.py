# ERP_CORE/attendance/permissions.py

from rest_framework import permissions

class IsAttendanceManagerOrReadOnly(permissions.BasePermission):
    """
    صلاحية مخصصة لإدارة الحضور والانصراف.
    فقط المشرفين والمديرين يمكنهم التعديل، والبقية قراءة فقط.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name__in=['Attendance Managers', 'HR Admins']).exists()
