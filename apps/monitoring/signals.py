# ERP_CORE/monitoring/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CapturedImage
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.alerts import trigger_risk_alert

@receiver(post_save, sender=CapturedImage)
def notify_ai_on_capture(sender, instance, created, **kwargs):
    if created:
        # ✅ تنبيه الذكاء الاصطناعي بتسجيل الالتقاط
        AIDecisionAlert.objects.create(
            section='monitoring',
            alert_type='📸 التقاط صورة منتج',
            message=f"تم التقاط صورة بتاريخ {instance.timestamp.strftime('%Y-%m-%d %H:%M')} بواسطة الكاميرا {instance.camera_id or 'غير محددة'}",
            level='info'
        )

        # ✅ تحذير داخلي إذا تم الالتقاط خارج أوقات العمل
        if instance.timestamp.hour < 7 or instance.timestamp.hour > 19:
            trigger_risk_alert(
                event="التقاط صورة خارج أوقات العمل",
                user=instance.captured_by if instance.captured_by else instance.camera_user,
                risk_level="MEDIUM",
                note=f"تم التقاط صورة في الساعة {instance.timestamp.strftime('%H:%M')}"
            )
