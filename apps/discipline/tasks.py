# ERP_CORE/discipline/tasks.py

from celery import shared_task
from django.utils.timezone import now
from .models import DisciplineRecord
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident
from datetime import timedelta

@shared_task
def check_frequent_disciplinary_actions():
    from apps.employees.models import Employee

    today = now().date()
    first_day = today.replace(day=1)
    employees = Employee.objects.all()

    for emp in employees:
        count = DisciplineRecord.objects.filter(employee=emp, date__gte=first_day).count()
        if count >= 3:
            # ✅ تنبيه مكرر تلقائيًا
            AIDecisionAlert.objects.get_or_create(
                section='discipline',
                alert_type='تكرار العقوبات',
                message=f"🚨 الموظف {emp.name} حصل على {count} عقوبات خلال هذا الشهر.",
                level='danger'
            )

            RiskIncident.objects.create(
                user=None,
                category="Discipline",
                event_type="تكرار العقوبات",
                risk_level="HIGH",
                notes=f"📌 تم رصد تكرار العقوبات للموظف {emp.name} ({count} عقوبات خلال شهر {first_day.strftime('%Y-%m')}).",
                reported_at=now()
            )
