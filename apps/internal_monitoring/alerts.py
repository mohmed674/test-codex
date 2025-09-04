# ERP_CORE/internal_monitoring/alerts.py

from django.contrib.auth.models import User
from django.core.mail import send_mail

# ✅ استيراد آمن لإرسال واتساب - يفترض أن whatsapp_bot مفعل
try:
    from apps.whatsapp_bot.utils import send_whatsapp_message
except ImportError:
    send_whatsapp_message = None


# ✅ إرسال تنبيه عند رصد خطر داخل النظام (مالي / مخزني / سلوكي...)
def trigger_risk_alert(event, user, risk_level, note):
    subject = f"[🚨 نظام ERP] تنبيه {risk_level.upper()} - {event}"
    message = (
        f"⚠️ تم رصد {risk_level} في النظام\n"
        f"📌 الحدث: {event}\n"
        f"👤 المستخدم: {getattr(user, 'username', 'غير معروف')}\n"
        f"📝 الملاحظات: {note}"
    )

    # ✅ إرسال بالبريد الإلكتروني
    send_mail(
        subject=subject,
        message=message,
        from_email="erp@system.local",
        recipient_list=["admin@company.com"],
        fail_silently=True,
    )

    # ✅ واتساب للمستخدم (إذا متاح)
    if (
        send_whatsapp_message
        and user
        and hasattr(user, "profile")
        and getattr(user.profile, "phone_number", None)
    ):
        try:
            send_whatsapp_message(user.profile.phone_number, message)
        except Exception:
            pass

    # ✅ واتساب للإدارة العليا (إذا متاح)
    if send_whatsapp_message:
        try:
            managers = User.objects.filter(is_superuser=True)
            for manager in managers:
                phone = getattr(getattr(manager, "profile", None), "phone_number", None)
                if phone:
                    send_whatsapp_message(phone, f"📢 {message}")
        except Exception:
            pass
