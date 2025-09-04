import importlib
import logging
from typing import Any, Optional

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.internal_monitoring.models import RiskIncident

from .models import Attendance

logger = logging.getLogger(__name__)

# Dynamic imports to keep runtime behavior while staying mypy-safe
_ai_models: Any = importlib.import_module("apps.ai_decision.models")
_payroll_models: Any = importlib.import_module("apps.payroll.models")

PerformanceAlert: Optional[Any] = getattr(_ai_models, "PerformanceAlert", None)
HourlyRateRecord: Optional[Any] = getattr(_payroll_models, "HourlyRateRecord", None)


@receiver(post_save, sender=Attendance)
def handle_attendance_created(
    sender, instance: Attendance, created: bool, **kwargs: Any
) -> None:
    if not created:
        return

    evaluation = instance.evaluation
    employee = evaluation.employee
    date = instance.date

    # ✅ 1. تسجيل أجر بالساعة تلقائيًا إذا العامل بنظام الساعات
    if getattr(employee, "contract_type", None) == "hourly":
        if HourlyRateRecord is not None:
            HourlyRateRecord.objects.create(
                employee=employee,
                date=date,
                hours=getattr(employee, "default_daily_hours", 0),
                rate_per_hour=getattr(
                    getattr(employee, "job_title", None), "default_hourly_rate", 0
                ),
            )
        else:
            logger.warning(
                "HourlyRateRecord model not available; skipped hourly rate record creation."
            )

    # ✅ 2. تحديث تقييم الالتزام
    if instance.status in {"absent", "late"}:
        evaluation.commitment_score = max(evaluation.commitment_score - 10, 0)
    evaluation.save(update_fields=["commitment_score"])

    # ✅ 3. تنبيه الذكاء الاصطناعي عند الغياب أو التأخير
    if instance.status in {"absent", "late"}:
        if PerformanceAlert is not None:
            PerformanceAlert.objects.create(
                employee=employee,
                issue_type="attendance",
                message=_("تم تسجيل {status} يوم {date}").format(
                    status=instance.status, date=date
                ),
                date=timezone.now(),
            )
        else:
            logger.warning(
                "PerformanceAlert model not available; skipped AI alert creation."
            )

        # ✅ 4. تسجيل المخالفة في سجل المراقبة الذكية
        RiskIncident.objects.create(
            user=getattr(employee, "user", None) if hasattr(employee, "user") else None,
            category="System",
            event_type=_("{etype} في الحضور").format(
                etype=_("غياب") if instance.status == "absent" else _("تأخير")
            ),
            risk_level="MEDIUM" if instance.status == "late" else "HIGH",
            notes=_("تم تسجيل {status} للموظف {employee} بتاريخ {date}").format(
                status=instance.status, employee=str(employee), date=date
            ),
        )
