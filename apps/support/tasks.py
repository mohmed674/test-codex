from celery import shared_task
from .models import SupportTicket
from django.utils import timezone
from datetime import timedelta

@shared_task
def escalate_unattended_tickets():
    limit = timezone.now() - timedelta(days=3)
    tickets = SupportTicket.objects.filter(status='open', created_at__lt=limit)
    for ticket in tickets:
        ticket.priority = 'high'
        ticket.save()
