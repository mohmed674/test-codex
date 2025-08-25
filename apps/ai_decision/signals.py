from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.production.models import ProductionOrder, ProductionStage
from apps.attendance.models import Attendance
from apps.ai_decision.models import DecisionLog
from apps.internal_monitoring.models import RiskIncident  # ✅ المراقبة الذكية
from django.utils import timezone
from datetime import timedelta

# ✅ 1. استقبال تنبيه من الإنتاج عند تأخر أو تعثر تنفيذ المرحلة
@receiver(post_save, sender=ProductionStage)
def analyze_stage_performance(sender, instance, created, **kwargs):
    if not created and instance.status == 'delayed':
        DecisionLog.objects.create(
            source='الإنتاج',
            level='تحذير',
            message=f"تأخر في مرحلة '{instance.stage_name}' لأمر تشغيل {instance.order.order_number}"
        )

        # ✅ تسجيل المخالفة في المراقبة
        RiskIncident.objects.create(
            user=instance.order.created_by if hasattr(instance.order, 'created_by') else None,
            category="Production",
            event_type="تأخير في مرحلة إنتاج",
            risk_level="MEDIUM",
            notes=f"مرحلة: {instance.stage_name} / رقم الأمر: {instance.order.order_number}"
        )


# ✅ 2. تنبيه تلقائي من الحضور في حالة تكرار الغياب أو التأخير
@receiver(post_save, sender=Attendance)
def analyze_attendance_pattern(sender, instance, created, **kwargs):
    if created and instance.status in ['متأخر', 'غياب']:
        recent = Attendance.objects.filter(employee=instance.employee, date__gte=timezone.now() - timedelta(days=7))
        late_or_absent_count = recent.filter(status__in=['غياب', 'متأخر']).count()

        if late_or_absent_count >= 3:
            DecisionLog.objects.create(
                source='الحضور',
                level='تحذير',
                message=f"الموظف {instance.employee} لديه {late_or_absent_count} حالات غياب/تأخير خلال أسبوع"
            )

            # ✅ تسجيل المخالفة
            RiskIncident.objects.create(
                user=instance.employee.user if hasattr(instance.employee, 'user') else None,
                category="System",
                event_type="غياب متكرر",
                risk_level="MEDIUM",
                notes=f"{late_or_absent_count} حالات غياب/تأخير للموظف: {instance.employee}"
            )


# ✅ 3. تحليل أداء الإنتاج وتسجيل نتائج تحليل أسبوعية
@receiver(post_save, sender=ProductionOrder)
def analyze_production_quality(sender, instance, created, **kwargs):
    if not created and instance.status == 'completed':
        DecisionLog.objects.create(
            source='الإنتاج',
            level='معلومة',
            message=f"تم إنهاء أمر إنتاج رقم {instance.order_number}، راجع الجودة والمخرجات"
        )

        # ✅ تسجيل في المراقبة كتحليل ختامي
        RiskIncident.objects.create(
            user=instance.created_by if hasattr(instance, 'created_by') else None,
            category="Production",
            event_type="إغلاق أمر إنتاج",
            risk_level="LOW",
            notes=f"تم إنهاء أمر إنتاج رقم: {instance.order_number}"
        )
