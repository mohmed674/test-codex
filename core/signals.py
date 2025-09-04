# core/signals.py
from __future__ import annotations

from contextlib import suppress
from typing import Any

from django.contrib.auth.models import User
from django.db import OperationalError, ProgrammingError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident


@receiver(
    post_save,
    sender=User,
    dispatch_uid="core_alert_ai_on_user_change",
)
def alert_ai_on_user_change(
    sender: type[User] | str, instance: User, created: bool, **kwargs: Any
) -> None:
    """
    عند إنشاء مستخدم جديد:
      - يرسل تنبيه للذكاء الاصطناعي.
      - يسجل حادثة مخاطرة داخلية.
    يتجاهل الأخطاء في حال الجداول غير جاهزة.
    """
    if not created:
        return

    # تنبيه AI (يتحمل غياب الجداول أثناء التهيئة/الهجرات)
    with suppress(ProgrammingError, OperationalError):
        AIDecisionAlert.objects.create(
            title=_("مستخدم جديد"),
            description=_("تم إنشاء مستخدم جديد بالاسم: %(username)s")
            % {"username": instance.username},
        )

    # تسجيل مخاطرة معلوماتية (يتحمل غياب الجداول أثناء التهيئة/الهجرات)
    with suppress(ProgrammingError, OperationalError):
        RiskIncident.objects.create(
            user=instance,
            category="System",
            event_type=_("إضافة مستخدم جديد للنظام"),
            risk_level="MEDIUM",
            notes=_("تم إنشاء حساب للمستخدم %(username)s - راجع الصلاحيات والإعدادات")
            % {"username": instance.username},
        )
