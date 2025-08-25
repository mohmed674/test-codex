from celery import shared_task
from .models import LegalCase
from django.utils import timezone
from datetime import timedelta

@shared_task
def alert_upcoming_sessions():
    today = timezone.now().date()
    upcoming = LegalCase.objects.filter(
        session_date__gte=today,
        session_date__lte=today + timedelta(days=7),
        status__in=['open', 'investigation']
    )
    for case in upcoming:
        print(f"🔔 تنبيه: جلسة قادمة لقضية '{case.title}' بتاريخ {case.session_date}")
