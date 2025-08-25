from rest_framework import permissions

class IsOwnerOrManager(permissions.BasePermission):
    """
    صلاحية تسمح بالوصول للمستخدم فقط على الإشعارات الخاصة به.
    وتسمح للمديرين (staff أو superuser) بالوصول الكامل.
    """

    def has_permission(self, request, view):
        # السماح فقط للمستخدمين المصادق عليهم
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # السماح للمديرين بالوصول الكامل
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # السماح للمستخدم فقط على إشعاراته
        return obj.user == request.user
