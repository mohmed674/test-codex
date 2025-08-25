# ERP_CORE/payroll/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TimeBasedSalaryRecord, PieceRateRecord
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.alerts import trigger_risk_alert

# ✅ 1. تنبيه عند تسجيل ساعات عمل زائدة
@receiver(post_save, sender=TimeBasedSalaryRecord)
def notify_ai_on_time_salary(sender, instance, created, **kwargs):
    if created:
        if instance.hours > 10:
            AIDecisionAlert.objects.create(
                section='payroll',
                alert_type='ساعات عمل زائدة',
                message=f"🔴 الموظف {instance.employee} عمل {instance.hours} ساعة في {instance.date}",
                level='warning'
            )

        # تنبيه داخلي في حال تجاوز حد العمل القانوني
        if instance.hours > 12:
            trigger_risk_alert(
                event="تجاوز ساعات العمل",
                user=instance.employee.user,
                risk_level="HIGH",
                note=f"تم تسجيل {instance.hours} ساعة للموظف {instance.employee} في يوم {instance.date}"
            )

# ✅ 2. تنبيه عند تسجيل كمية إنتاج استثنائية بنظام القطعة
@receiver(post_save, sender=PieceRateRecord)
def notify_ai_on_piece_rate(sender, instance, created, **kwargs):
    if created and instance.quantity > 1000:
        AIDecisionAlert.objects.create(
            section='payroll',
            alert_type='إنتاج غير اعتيادي',
            message=f"⚠️ {instance.employee} سجل {instance.quantity} قطعة في {instance.date}",
            level='info'
        )
