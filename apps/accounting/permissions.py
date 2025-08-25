from rest_framework import permissions

class IsAccountingManagerOrReadOnly(permissions.BasePermission):
    """
    🔐 صلاحيات المحاسبة – قراءة فقط لغير المدير، وتعديل للمدير أو المحاسب.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.has_perm('accounting.view_journalentry')
        return (
            request.user.has_perm('accounting.change_journalentry') or
            request.user.has_perm('accounting.add_journalentry')
        )
