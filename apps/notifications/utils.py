# notifications/utils.py

from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings

def notify_user_group(group_name, message):
    """
    إرسال إشعار جماعي لمجموعة معينة من المستخدمين
    """
    group = Group.objects.filter(name=group_name).first()
    if group:
        for user in group.user_set.all():
            if user.email:
                send_mail(
                    subject="إشعار من النظام",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )
