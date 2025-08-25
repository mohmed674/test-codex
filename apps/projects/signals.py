from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from apps.notifications.models import Notification  # يفترض وجود نظام إشعارات

@receiver(post_save, sender=Task)
def notify_task_assignment(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        Notification.objects.create(
            user=instance.assigned_to.user,
            message=f"تم تعيينك على مهمة: {instance.title} ضمن المشروع {instance.project.name}"
        )
