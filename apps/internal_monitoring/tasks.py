# ERP_CORE/internal_monitoring/tasks.py
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


def reactivate_suspended_users() -> None:
    """
    إعادة تفعيل المستخدمين الذين انتهت فترة الإيقاف الخاصة بهم.
    يتحقق من وجود الحقل `suspension_end` سواء على User مباشرة أو عبر Profile.
    """
    for user in User.objects.filter(is_active=False):
        # قد يكون الحقل على User أو على Profile (OneToOne)
        suspension_end = getattr(user, "suspension_end", None)

        # تفادي تحذير المحلل الساكن: لا نستخدم hasattr ثم dot-access
        profile = getattr(user, "profile", None)
        if suspension_end is None and profile is not None:
            suspension_end = getattr(profile, "suspension_end", None)

        if suspension_end and suspension_end <= timezone.now():
            user.is_active = True
            user.save()
