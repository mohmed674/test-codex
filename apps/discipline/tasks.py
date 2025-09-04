# ERP_CORE/discipline/tasks.py
from __future__ import annotations

"""
Celery task to detect employees with frequent disciplinary actions within the current month and
raise AI decision alerts and risk incidents accordingly.

Improvements:
- Avoid N+1 queries by aggregating DisciplineRecord per employee in a single query.
- Use emp.pk instead of emp.id to satisfy static analyzers while preserving behavior.
- Keep behavior (create/get_or_create) and messages intact.
"""

from celery import shared_task
from django.db.models import Count
from django.utils.timezone import now

from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident

from .models import DisciplineRecord


@shared_task
def check_frequent_disciplinary_actions() -> None:
    """
    For the current month, find employees with >=3 disciplinary records and:
      - create/get an AI decision alert,
      - create a RiskIncident entry.
    """
    from apps.employees.models import \
        Employee  # Local import to avoid circular imports at worker boot

    today = now().date()
    first_day = today.replace(day=1)

    # Aggregate counts per employee for this month in one query
    monthly_counts = (
        DisciplineRecord.objects.filter(date__gte=first_day)
        .values("employee")
        .annotate(total=Count("id"))
        .filter(total__gte=3)
    )

    # Map employee_id -> total
    emp_totals = {
        row["employee"]: int(row["total"]) for row in monthly_counts if row["employee"]
    }

    if not emp_totals:
        return

    # Fetch only needed employees (explicit type helps IDE/mypy for emp.pk below)
    employees: list[Employee] = list(
        Employee.objects.filter(id__in=emp_totals.keys()).only("id", "name")
    )

    for emp in employees:
        count = emp_totals.get(int(emp.pk), 0)
        # Name fallback to string representation if 'name' missing
        emp_name = getattr(emp, "name", None) or str(emp)

        # ✅ Create or get alert
        AIDecisionAlert.objects.get_or_create(
            section="discipline",
            alert_type="تكرار العقوبات",
            message=f"🚨 الموظف {emp_name} حصل على {count} عقوبات خلال هذا الشهر.",
            level="danger",
        )

        # Log risk incident
        RiskIncident.objects.create(
            user=None,
            category="Discipline",
            event_type="تكرار العقوبات",
            risk_level="HIGH",
            notes=(
                "📌 تم رصد تكرار العقوبات للموظف "
                f"{emp_name} ({count} عقوبات خلال شهر {first_day.strftime('%Y-%m')})."
            ),
            reported_at=now(),
        )
