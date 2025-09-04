# apps/accounting/permissions.py
from rest_framework import permissions


class IsAccountingManagerOrReadOnly(permissions.BasePermission):
    """
    🔐 صلاحيات المحاسبة:
    - للزوار/المستخدمين العاديين → قراءة فقط (GET, HEAD, OPTIONS).
    - للمديرين أو من لديهم صلاحيات تعديل/إضافة → يسمح بالعمليات الكاملة.
    """

    def has_permission(self, request, view) -> bool:
        # 🟢 السماح بالعمليات الآمنة لو عنده إذن عرض
        if request.method in permissions.SAFE_METHODS:
            return request.user.has_perm("accounting.view_journalentry")

        # 🔵 السماح بالإنشاء/التعديل لو عنده صلاحيات مناسبة
        return request.user.has_perm(
            "accounting.change_journalentry"
        ) or request.user.has_perm("accounting.add_journalentry")
