from celery import shared_task
from .models import Shipment
from django.utils import timezone

@shared_task
def mark_delayed_shipments():
    shipments = Shipment.objects.filter(
        status='in_transit',
        shipping_date__lt=timezone.now() - timezone.timedelta(days=7)
    )
    for shipment in shipments:
        shipment.status = 'failed'
        shipment.save()
