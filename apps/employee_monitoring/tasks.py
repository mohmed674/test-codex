# ERP_CORE/employee_monitoring/tasks.py

from celery import shared_task
from .models import MonitoringRecord
from django.utils import timezone
from apps.ai_decision.models import AIDecisionAlert

@shared_task
def daily_monitoring_summary():
    today = timezone.now().date()
    records_today = MonitoringRecord.objects.filter(date__date=today)

    if not records_today.exists():
        AIDecisionAlert.objects.create(
            section="employee_monitoring",
            alert_type="غياب متابعة",
            message="لم يتم إدخال أي سجل متابعة اليوم.",
            level='warning'
        )
