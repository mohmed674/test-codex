from __future__ import annotations

from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.ai_decision.models import AIDecisionLog  # ✅ الاسم الصحيح
from apps.attendance.models import Attendance
from apps.internal_monitoring.models import RiskIncident
from apps.production.models import ProductionOrder, ProductionStage


# ✅ 1. استقبال تنبيه من الإنتاج عند تأخر أو تعثر تنفيذ المرحلة
@receiver(post_save, sender=ProductionStage)
def analyze_stage_performance(sender, instance, created, **kwargs):
    """Log delay in a production stage and create a RiskIncident."""
    if not created and instance.status == "delayed":
        msg = _("تأخر في مرحلة '{stage}' لأمر تشغيل {order}").format(
            stage=instance.stage_name, order=instance.order.order_number
        )

        AIDecisionLog.objects.create(
            user=getattr(instance.order, "created_by", None),
            event_type="تأخير مرحلة إنتاج",
            description=msg,
            risk_level="Medium",
        )

        notes = _("مرحلة: {stage} / رقم الأمر: {order}").format(
            stage=instance.stage_name, order=instance.order.order_number
        )

        RiskIncident.objects.create(
            user=getattr(instance.order, "created_by", None),
            category="Production",
            event_type="تأخير في مرحلة إنتاج",
            risk_level="MEDIUM",
            notes=notes,
        )


# ✅ 2. تنبيه تلقائي من الحضور في حالة تكرار الغياب أو التأخير
@receiver(post_save, sender=Attendance)
def analyze_attendance_pattern(sender, instance, created, **kwargs):
    """Detect frequent absence/late and create AIDecisionLog + RiskIncident."""
    if created and instance.status in ["متأخر", "غياب"]:
        recent = Attendance.objects.filter(
            employee=instance.employee,
            date__gte=timezone.now() - timedelta(days=7),
        )
        late_or_absent_count = recent.filter(status__in=["غياب", "متأخر"]).count()

        if late_or_absent_count >= 3:
            msg = _("الموظف {emp} لديه {count} حالات غياب/تأخير خلال أسبوع").format(
                emp=instance.employee, count=late_or_absent_count
            )

            AIDecisionLog.objects.create(
                user=getattr(instance.employee, "user", None),
                event_type="غياب متكرر",
                description=msg,
                risk_level="Medium",
            )

            notes = _("{count} حالات غياب/تأخير للموظف: {emp}").format(
                count=late_or_absent_count, emp=instance.employee
            )

            RiskIncident.objects.create(
                user=getattr(instance.employee, "user", None),
                category="System",
                event_type="غياب متكرر",
                risk_level="MEDIUM",
                notes=notes,
            )


# ✅ 3. تحليل أداء الإنتاج وتسجيل نتائج تحليل أسبوعية
@receiver(post_save, sender=ProductionOrder)
def analyze_production_quality(sender, instance, created, **kwargs):
    """On order completion, log summary and create a closing RiskIncident."""
    if not created and instance.status == "completed":
        msg = _("تم إنهاء أمر إنتاج رقم {order}، راجع الجودة والمخرجات").format(
            order=instance.order_number
        )

        AIDecisionLog.objects.create(
            user=getattr(instance, "created_by", None),
            event_type="إغلاق أمر إنتاج",
            description=msg,
            risk_level="Low",
        )

        notes = _("تم إنهاء أمر إنتاج رقم: {order}").format(order=instance.order_number)

        RiskIncident.objects.create(
            user=getattr(instance, "created_by", None),
            category="Production",
            event_type="إغلاق أمر إنتاج",
            risk_level="LOW",
            notes=notes,
        )
