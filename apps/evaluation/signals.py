# ERP_CORE/evaluation/signals.py
from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.ai_decision.models import AIDecisionAlert
from apps.attendance.models import Attendance
from apps.evaluation.models import Evaluation
from apps.internal_monitoring.models import RiskIncident
from apps.production.models import ProductionOrder


def _get_num(obj: object, field: str, default: float = 0.0) -> float:
    """قراءة قيمة رقمية من كائن بشكل آمن."""
    try:
        return float(getattr(obj, field, default) or 0)
    except Exception:
        return float(default)


def _set_num(obj: object, field: str, value: float) -> None:
    """تعيين قيمة رقمية في كائن بشكل آمن."""
    try:
        setattr(obj, field, float(value))
    except Exception:
        # تجاهل بصمت إن لم يكن الحقل موجود
        return


# ✅ 1) ربط الحضور بتقييم الانضباط + تنبيهات ذكية + مراقبة مخاطر
@receiver(post_save, sender=Attendance)
def update_evaluation_from_attendance(
    sender, instance: Attendance, created: bool, **kwargs
) -> None:
    employee = getattr(instance, "employee", None)
    if not created or employee is None:
        return

    eval_obj, _ = Evaluation.objects.get_or_create(employee=employee)

    event_type: str | None = None
    risk_level: str = "LOW"

    # قراءة القيم الحالية من Evaluation
    current_punctuality = _get_num(eval_obj, "punctuality_score", 0.0)
    status = getattr(instance, "status", "")

    if status == "absent":
        _set_num(eval_obj, "punctuality_score", max(0.0, current_punctuality - 1.0))
        event_type = "غياب بدون إذن"
        risk_level = "MEDIUM"
        AIDecisionAlert.objects.create(
            section="attendance",
            alert_type=event_type,
            message=f"غياب {employee} في {getattr(instance, 'date', '')}",
            level="warning",
        )
    elif status == "late":
        _set_num(eval_obj, "punctuality_score", max(0.0, current_punctuality - 0.5))
        event_type = "تأخير في الحضور"
    else:
        _set_num(
            eval_obj, "punctuality_score", current_punctuality + 0.25
        )  # حضور ممتاز

    eval_obj.save()

    if event_type:
        RiskIncident.objects.create(
            user=getattr(instance, "recorded_by", None),
            category="System",
            event_type=event_type,
            risk_level=risk_level,
            notes=f"تم تسجيل {event_type} للموظف {employee} بتاريخ {getattr(instance, 'date', '')}",
        )


# ✅ 2) ربط الإنتاج بتقييم الأداء + ذكاء صناعي + سجل المراقبة
@receiver(post_save, sender=ProductionOrder)
def update_evaluation_from_production(
    sender, instance: ProductionOrder, created: bool, **kwargs
) -> None:
    assigned = getattr(instance, "assigned_to", None)
    if not created or assigned is None:
        return

    try:
        assignees = assigned.all()
    except Exception:
        return

    for emp in assignees:
        eval_obj, _ = Evaluation.objects.get_or_create(employee=emp)
        current_perf = _get_num(eval_obj, "performance_score", 0.0)
        _set_num(eval_obj, "performance_score", current_perf + 1.0)
        eval_obj.save()

        order_number = getattr(instance, "order_number", "")
        AIDecisionAlert.objects.create(
            section="production",
            alert_type="إنتاج عالي",
            message=f"{emp} شارك في أمر إنتاج {order_number}",
            level="info",
        )

        RiskIncident.objects.create(
            user=None,
            category="Production",
            event_type="مشاركة في أمر إنتاج",
            risk_level="LOW",
            notes=f"تم تسجيل مشاركة {emp} في أمر إنتاج رقم {order_number}",
        )
