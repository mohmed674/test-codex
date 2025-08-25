from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lead
from apps.clients.models import Client

@receiver(post_save, sender=Lead)
def convert_lead_to_client(sender, instance, **kwargs):
    if instance.status == 'converted':
        Client.objects.get_or_create(
            name=instance.name,
            defaults={
                'phone': instance.phone,
                'email': instance.email,
                'source': instance.source
            }
        )
