from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BackupRecord
from django.core.mail import send_mail
from django.conf import settings
from apps.whatsapp_bot.utils import send_whatsapp_message  # يفترض وجود التطبيق

@receiver(post_save, sender=BackupRecord)
def notify_backup_status(sender, instance, created, **kwargs):
    if created:
        subject = f"✅ Backup Completed: {instance.file_type}"
        message = f"A new backup was created at {instance.created_at}.\nFile: {instance.file_path}"
        recipients = [settings.ADMIN_EMAIL]  # تأكد من وجود هذا الإعداد
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)

        try:
            send_whatsapp_message(f"✅ [ERP Backup]\nType: {instance.file_type}\nTime: {instance.created_at}", to="admin")
        except Exception:
            pass  # يمكن تسجيل الخطأ لاحقًا
