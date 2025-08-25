from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Department
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident, ReportLog
from django.utils.timezone import now
from core.utils import log_user_action


@receiver(post_save, sender=Department)
def notify_ai_on_department_change(sender, instance, created, **kwargs):
    AIDecisionAlert.objects.create(
        section='departments',
        alert_type='إنشاء قسم جديد' if created else 'تحديث قسم',
        message=f"تم {'إضافة' if created else 'تحديث'} قسم: {instance.name}",
        level='info',
        timestamp=now()
    )

    RiskIncident.objects.create(
        user=None,
        category="System",
        event_type="إنشاء قسم جديد" if created else "تعديل قسم",
        risk_level="LOW" if created else "MEDIUM",
        notes=f"تم {'إضافة' if created else 'تعديل'} قسم {instance.name} في النظام.",
        reported_at=now()
    )

    ReportLog.objects.create(
        model='Department',
        action='Create' if created else 'Update',
        ref=str(instance.pk),
        notes=f"{'أُنشئ' if created else 'تحديث'} قسم: {instance.name}",
        timestamp=now()
    )

    # ✅ تتبع المستخدم عند وجوده (قابل للتوسيع مستقبلاً)
    log_user_action(
        model='Department',
        action='create' if created else 'update',
        instance_id=instance.pk,
        description=f"{'إضافة' if created else 'تعديل'} قسم {instance.name}"
    )


@receiver(pre_delete, sender=Department)
def notify_on_department_deletion(sender, instance, **kwargs):
    AIDecisionAlert.objects.create(
        section='departments',
        alert_type='حذف قسم',
        message=f"🚫 تم حذف القسم: {instance.name}",
        level='warning',
        timestamp=now()
    )

    RiskIncident.objects.create(
        user=None,
        category="System",
        event_type="حذف قسم",
        risk_level="HIGH",
        notes=f"⚠️ حذف القسم: {instance.name} من النظام.",
        reported_at=now()
    )

    ReportLog.objects.create(
        model='Department',
        action='Delete',
        ref=str(instance.pk),
        notes=f"🚨 تم حذف قسم: {instance.name}",
        timestamp=now()
    )

    log_user_action(
        model='Department',
        action='delete',
        instance_id=instance.pk,
        description=f"حذف قسم {instance.name}"
    )
