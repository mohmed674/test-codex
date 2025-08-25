# ERP_CORE/internal_monitoring/alerts.py

from django.core.mail import send_mail
from django.contrib.auth.models import User

# ✅ استيراد آمن لإرسال واتساب - يفترض أن whatsapp_bot مفعل
try:
    from apps.whatsapp_bot.utils import send_whatsapp_message
except ImportError:
    send_whatsapp_message = None

# ✅ إرسال تنبيه عند رصد خطر داخل النظام (مالي / مخزني / سلوكي...)
def trigger_risk_alert(event, user, risk_level, note):
    subject = f'[🚨 نظام ERP] تنبيه {risk_level.upper()} - {event}'
    message = (
        f"⚠️ تم رصد {risk_level} في النظام\n"
        f"📌 الحدث: {event}\n"
        f"👤 المستخدم: {user.username if user else 'غير معروف'}\n"
        f"📝 الملاحظات: {note}"
    )

    # ✅ إرسال بالبريد الإلكتروني
    send_mail(
        subject=subject,
        message=message,
        from_email='erp@system.local',
        recipient_list=['admin@company.com'],
        fail_silently=True
    )

    # ✅ واتساب للمستخدم (إذا متاح)
    if send_whatsapp_message and user and hasattr(user, 'profile') and user.profile.phone_number:
        send_whatsapp_message(user.profile.phone_number, message)

    # ✅ واتساب للإدارة العليا (إذا متاح)
    if send_whatsapp_message:
        try:
            managers = User.objects.filter(is_superuser=True)
            for manager in managers:
                if hasattr(manager, 'profile') and manager.profile.phone_number:
                    send_whatsapp_message(manager.profile.phone_number, f"📢 {message}")
        except Exception:
            pass
