from rest_framework import permissions

class IsSurveyAdminOrReadOnly(permissions.BasePermission):
    """
    يسمح فقط لمشرف الاستبيان بالتعديل، والباقي عرض فقط.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
