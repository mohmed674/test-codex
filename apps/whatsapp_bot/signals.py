# ERP_CORE/whatsapp_bot/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WhatsAppOrder
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident

@receiver(post_save, sender=WhatsAppOrder)
def handle_new_whatsapp_order(sender, instance, created, **kwargs):
    if created:
        user = instance.created_by if hasattr(instance, 'created_by') else None

        # ✅ 1. تنبيه الذكاء الاصطناعي
        AIDecisionAlert.objects.create(
            section='whatsapp_bot',
            alert_type='طلب جديد عبر واتساب',
            message=f"📩 طلب واتساب من العميل: {instance.client_name} - المنتج: {instance.product_requested}",
            level='info'
        )

        # ✅ 2. تسجيل مخاطرة ذكية عند الشك في الطلب (مثال: كمية غير طبيعية أو عميل غير نشط)
        if instance.quantity > 100 or instance.status == 'معلق':
            RiskIncident.objects.create(
                user=user,
                category="WhatsApp",
                event_type="طلب غير معتاد",
                risk_level="MEDIUM",
                notes=f"طلب بكمية كبيرة أو في حالة غير معتادة: {instance.quantity} وحدة من {instance.product_requested}"
            )
