# ERP_CORE/maintenance/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.production.models import ProductionStage
from apps.maintenance.models import MaintenanceLog, Machine
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident
from django.utils import timezone
from datetime import timedelta

# ✅ تسجيل استهلاك وتشغيل الماكينات
@receiver(post_save, sender=ProductionStage)
def log_machine_usage_on_stage_completion(sender, instance, created, **kwargs):
    if created or instance.status != 'completed' or not instance.machine:
        return

    machine = instance.machine
    duration = (instance.end_time - instance.start_time).total_seconds() / 3600  # بالساعات

    # ✅ إنشاء سجل صيانة بالتشغيل
    MaintenanceLog.objects.create(
        machine=machine,
        issue=f"تشغيل لمدة {round(duration, 2)} ساعة",
        date_reported=timezone.now(),
        status='تم التشغيل',
        notes=f"تم تشغيل {machine.name} خلال مرحلة {instance.stage_name}"
    )

    # ✅ تحديث ساعات التشغيل الكلية
    machine.operating_hours += duration
    machine.last_used_at = timezone.now()
    machine.save()

    # ⏳ تنبيه إذا تجاوزت ساعات التشغيل حد الصيانة
    if machine.operating_hours >= machine.maintenance_threshold:
        # سجل صيانة تنبيهي
        MaintenanceLog.objects.create(
            machine=machine,
            issue="⚠️ تنبيه: الماكينة تجاوزت حد التشغيل المسموح به",
            date_reported=timezone.now(),
            status='تنبيه',
            notes="تجاوز ساعات التشغيل دون صيانة دورية"
        )

        # تنبيه AI
        AIDecisionAlert.objects.create(
            section='maintenance',
            alert_type='صيانة دورية متأخرة',
            message=f"الماكينة {machine.name} تجاوزت حد التشغيل ({round(machine.operating_hours, 2)} ساعة)",
            level='warning'
        )

        # تسجيل خطر في المراقبة
        RiskIncident.objects.create(
            user=None,
            category='System',
            event_type='تجاوز صيانة دورية',
            risk_level='MEDIUM',
            notes=f"الماكينة {machine.name} تجاوزت حد التشغيل المسموح ({machine.maintenance_threshold} ساعة)"
        )
