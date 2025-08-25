# ERP_CORE/pattern/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pattern
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident

@receiver(post_save, sender=Pattern)
def notify_ai_and_risk_on_pattern_change(sender, instance, created, **kwargs):
    user = getattr(instance, 'modified_by', None)

    # ✅ 1. تنبيه الذكاء الاصطناعي
    AIDecisionAlert.objects.create(
        section='pattern',
        alert_type='تعديل باترون' if not created else 'إنشاء باترون جديد',
        message=f"{'تعديل' if not created else 'إضافة'} باترون: {instance.name}",
        level='info' if created else 'warning'
    )

    # ✅ 2. تسجيل مخاطرة عند تعديل باترون حرج أو بدون صلاحية
    if not created and instance.is_critical:
        RiskIncident.objects.create(
            user=user,
            category="Pattern",
            event_type="تعديل باترون حرج",
            risk_level="HIGH",
            notes=f"تم تعديل الباترون الحرج: {instance.name}"
        )
