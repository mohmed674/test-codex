# ERP_CORE/core/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import ProgrammingError, OperationalError
from apps.internal_monitoring.models import RiskIncident
from apps.ai_decision.models import AIDecisionAlert

@receiver(post_save, sender=User)
def alert_ai_on_user_change(sender, instance, created, **kwargs):
    if created:
        # تنبيه AI (يتجاهل لو الجدول لسه متعملش)
        try:
            AIDecisionAlert.objects.create(
                title="مستخدم جديد",
                description=f"تم إنشاء مستخدم جديد بالاسم: {instance.username}",
            )
        except (ProgrammingError, OperationalError):
            # قاعدة البيانات/الجداول غير جاهزة بعد
            pass

        # تسجيل مخاطرة معلوماتية (آمنة)
        try:
            RiskIncident.objects.create(
                user=instance,
                category="System",
                event_type="إضافة مستخدم جديد للنظام",
                risk_level="MEDIUM",
                notes=f"تم إنشاء حساب للمستخدم {instance.username} - راجع الصلاحيات والإعدادات",
            )
        except (ProgrammingError, OperationalError):
            pass
