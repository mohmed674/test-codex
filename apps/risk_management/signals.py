from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Risk
from apps.whatsapp_bot.api_views import send_message

@receiver(post_save, sender=Risk)
def notify_critical_risk(sender, instance, created, **kwargs):
    if created and instance.severity in ['high', 'critical']:
        msg = f"⚠️ خطر جديد: {instance.title}\nالخطورة: {instance.get_severity_display()}"
        send_message('+201234567890', msg)  # رقم مدير النظام
