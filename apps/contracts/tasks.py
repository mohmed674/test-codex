from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import Contract


@shared_task
def alert_contracts_expiring():
    today = timezone.now().date()
    alert_range = today + timedelta(days=15)
    expiring_contracts = Contract.objects.filter(
        end_date__lte=alert_range, end_date__gte=today
    )
    for contract in expiring_contracts:
        print(f"🔔 تنبيه: عقد '{contract.title}' سينتهي في {contract.end_date}")
