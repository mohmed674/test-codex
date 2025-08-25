# ERP_CORE/employee_monitoring/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DataLogMonitor
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident  # ✅ سجل المراقبة الذكي

@receiver(post_save, sender=DataLogMonitor)
def alert_ai_on_monitor_log(sender, instance, created, **kwargs):
    if instance.entry_status == 'error':
        # ✅ تنبيه الذكاء الاصطناعي
        AIDecisionAlert.objects.create(
            section='monitoring',
            alert_type='فشل دخول',
            message=f"فشل دخول {instance.user} في {instance.section}",
            level='high'
        )

        # ✅ تسجيل مخالفة أمنية في نظام المراقبة الذكي
        RiskIncident.objects.create(
            user=instance.user,
            category="System",
            event_type="محاولة دخول غير ناجحة",
            risk_level="HIGH",
            notes=f"تم رصد محاولة دخول فاشلة في القسم: {instance.section}"
        )
