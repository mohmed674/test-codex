from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import POSOrder
from apps.accounting.models import AccountingEntry

@receiver(post_save, sender=POSOrder)
def create_accounting_entry(sender, instance, created, **kwargs):
    if created:
        AccountingEntry.objects.create(
            description=f"POS Order #{instance.id}",
            amount=instance.total,
            entry_type='credit',
            related_order=instance
        )
