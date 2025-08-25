from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Attendance
from apps.payroll.models import HourlyRateRecord
from apps.evaluation.models import Evaluation
from apps.ai_decision.models import PerformanceAlert
from apps.internal_monitoring.models import RiskIncident  # ✅ نظام المراقبة الذكي
from django.utils import timezone

@receiver(post_save, sender=Attendance)
def handle_attendance_created(sender, instance, created, **kwargs):
    if created:
        evaluation = instance.evaluation
        employee = evaluation.employee
        date = instance.date

        # ✅ 1. تسجيل أجر بالساعة تلقائيًا إذا العامل بنظام الساعات
        if employee.contract_type == 'hourly':
            HourlyRateRecord.objects.create(
                employee=employee,
                date=date,
                hours=employee.default_daily_hours,
                rate_per_hour=employee.job_title.default_hourly_rate
            )

        # ✅ 2. تحديث تقييم الالتزام
        evaluation.commitment_score = max(evaluation.commitment_score - 10, 0) if instance.status in ["absent", "late"] else evaluation.commitment_score
        evaluation.save()

        # ✅ 3. تنبيه الذكاء الاصطناعي عند الغياب أو التأخير
        if instance.status in ["absent", "late"]:
            PerformanceAlert.objects.create(
                employee=employee,
                issue_type="attendance",
                message=f"تم تسجيل {instance.status} يوم {date}",
                date=timezone.now()
            )

            # ✅ 4. تسجيل المخالفة في سجل المراقبة الذكية
            RiskIncident.objects.create(
                user=employee.user if hasattr(employee, 'user') else None,
                category="System",
                event_type=f"{'غياب' if instance.status == 'absent' else 'تأخير'} في الحضور",
                risk_level="MEDIUM" if instance.status == "late" else "HIGH",
                notes=f"تم تسجيل {instance.status} للموظف {employee} بتاريخ {date}"
            )
