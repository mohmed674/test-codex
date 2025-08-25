from celery import shared_task
from .models import Task
from django.utils import timezone
from datetime import timedelta

@shared_task
def alert_overdue_tasks():
    today = timezone.now().date()
    overdue = Task.objects.filter(due_date__lt=today, status__in=['todo', 'doing'])
    for task in overdue:
        print(f"⚠️ مهمة متأخرة: {task.title} - مخصصة لـ {task.assigned_to}")
