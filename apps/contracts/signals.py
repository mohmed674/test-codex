from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.models import Notification  # يفترض وجود نظام إشعارات

from .models import Contract


@receiver(post_save, sender=Contract)
def notify_contract_creation(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            message=f"تم إنشاء عقد جديد: {instance.title}", group="Legal"
        )
