from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.models import Notification  # يفترض وجود نظام إشعارات

from .models import Campaign


@receiver(post_save, sender=Campaign)
def notify_marketing_team(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            message=f"تم إنشاء حملة جديدة: {instance.name}", group="Marketing"
        )
