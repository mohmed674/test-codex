# ERP_CORE/employees/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident  # ✅ إضافة سجل المراقبة

@receiver(post_save, sender=Employee)
def alert_ai_on_employee_change(sender, instance, created, **kwargs):
    if created:
        # ✅ تنبيه AI عند إضافة موظف
        AIDecisionAlert.objects.create(
            section='employees',
            alert_type='موظف جديد',
            message=f"تم تسجيل موظف جديد: {instance.name}",
            level='info'
        )

        # ✅ تسجيل الحدث في سجل المخاطر
        RiskIncident.objects.create(
            user=instance.created_by if hasattr(instance, 'created_by') else None,
            category='System',
            event_type='إضافة موظف جديد',
            risk_level='LOW',
            notes=f"تمت إضافة الموظف {instance.name} إلى النظام"
        )
