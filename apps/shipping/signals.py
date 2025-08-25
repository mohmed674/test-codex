from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Shipment
from apps.accounting.models import AccountingEntry

@receiver(post_save, sender=Shipment)
def create_shipping_cost_entry(sender, instance, created, **kwargs):
    if created and instance.cost > 0:
        AccountingEntry.objects.create(
            description=f"تكلفة شحن {instance.tracking_number}",
            amount=instance.cost,
            entry_type='debit',
            related_invoice=instance.invoice
        )
