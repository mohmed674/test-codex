# ERP_CORE/departments/ai.py
from .models import Department
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Department)
def department_monitor(sender, instance, created, **kwargs):
    # ✅ تنبيه عند تجاوز الحد الأقصى المقترح للموظفين
    if hasattr(instance, 'employee_count') and instance.employee_count > 50:
        AIDecisionAlert.objects.create(
            section="departments",
            alert_type="عدد موظفين مرتفع",
            level="warning",
            message=f"📢 القسم {instance.name} تجاوز 50 موظفًا، يُنصح بإعادة التوزيع."
        )
        RiskIncident.objects.create(
            user=None,
            category="تنظيم إداري",
            event_type="كثافة موظفين",
            risk_level="MEDIUM",
            notes=f"📈 رُصد قسم {instance.name} بعدد موظفين يتجاوز 50. يجب المراجعة."
        )

    # ✅ تنبيه ذكي عند التعديل أو الإنشاء العام
    alert_type = "قسم جديد" if created else "تحديث قسم"
    level = "info" if created else "low"
    AIDecisionAlert.objects.create(
        section="departments",
        alert_type=alert_type,
        level=level,
        message=f"📂 تم {'إضافة' if created else 'تحديث'} قسم: {instance.name}"
    )
