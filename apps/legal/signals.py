from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.models import Notification  # يفترض وجود نظام إشعارات

from .models import LegalCase


@receiver(post_save, sender=LegalCase)
def notify_legal_case_created(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            message=f"📂 قضية قانونية جديدة: {instance.title}", group="Legal"
        )
