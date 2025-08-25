from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SupportTicket
from apps.notifications.models import Notification  # يفترض وجود تطبيق إشعارات

@receiver(post_save, sender=SupportTicket)
def notify_assigned_support(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        Notification.objects.create(
            user=instance.assigned_to.user,
            message=f"تم تعيينك لمتابعة طلب دعم رقم #{instance.id}"
        )
