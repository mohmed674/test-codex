from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import SupportTicket


@shared_task
def escalate_unattended_tickets():
    limit = timezone.now() - timedelta(days=3)
    tickets = SupportTicket.objects.filter(status="open", created_at__lt=limit)
    for ticket in tickets:
        ticket.priority = "high"
        ticket.save()
