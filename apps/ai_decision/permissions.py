# ERP_CORE/ai_decision/permissions.py

from rest_framework import permissions

class IsAIManagerOrReadOnly(permissions.BasePermission):
    """
    صلاحية: تسمح فقط لمدير الذكاء أو المشرفين بالتعديل، والباقي قراءة فقط.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name__in=['AI Managers', 'System Auditors']).exists()
