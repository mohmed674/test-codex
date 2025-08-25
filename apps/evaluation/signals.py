# ERP_CORE/evaluation/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.attendance.models import Attendance
from apps.production.models import ProductionOrder
from apps.evaluation.models import Evaluation
from django.utils import timezone
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident  # ✅ إضافة نظام المراقبة

# ✅ 1. ربط الحضور بتقييم الانضباط + تنبيهات ذكية + مراقبة مخاطر
@receiver(post_save, sender=Attendance)
def update_evaluation_from_attendance(sender, instance, created, **kwargs):
    if created and instance.employee:
        eval_obj, _ = Evaluation.objects.get_or_create(employee=instance.employee)
        event_type = None
        risk_level = 'LOW'

        if instance.status == 'absent':
            eval_obj.punctuality_score = max(0, eval_obj.punctuality_score - 1)
            event_type = "غياب بدون إذن"
            risk_level = "MEDIUM"
            AIDecisionAlert.objects.create(
                section='attendance',
                alert_type=event_type,
                message=f"غياب {instance.employee} في {instance.date}",
                level='warning'
            )
        elif instance.status == 'late':
            eval_obj.punctuality_score = max(0, eval_obj.punctuality_score - 0.5)
            event_type = "تأخير في الحضور"
        else:
            eval_obj.punctuality_score += 0.25  # حضور ممتاز

        eval_obj.save()

        if event_type:
            RiskIncident.objects.create(
                user=instance.recorded_by if hasattr(instance, 'recorded_by') else None,
                category='System',
                event_type=event_type,
                risk_level=risk_level,
                notes=f"تم تسجيل {event_type} للموظف {instance.employee} بتاريخ {instance.date}"
            )


# ✅ 2. ربط الإنتاج بتقييم الأداء + ذكاء صناعي + سجل المراقبة
@receiver(post_save, sender=ProductionOrder)
def update_evaluation_from_production(sender, instance, created, **kwargs):
    if created and instance.assigned_to.exists():
        for emp in instance.assigned_to.all():
            eval_obj, _ = Evaluation.objects.get_or_create(employee=emp)
            eval_obj.performance_score += 1
            eval_obj.save()

            AIDecisionAlert.objects.create(
                section='production',
                alert_type='إنتاج عالي',
                message=f"{emp} شارك في أمر إنتاج {instance.order_number}",
                level='info'
            )

            RiskIncident.objects.create(
                user=None,
                category='Production',
                event_type='مشاركة في أمر إنتاج',
                risk_level='LOW',
                notes=f"تم تسجيل مشاركة {emp} في أمر إنتاج رقم {instance.order_number}"
            )
