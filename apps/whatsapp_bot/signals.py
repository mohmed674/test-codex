# ERP_CORE/whatsapp_bot/signals.py
from __future__ import annotations

import logging
from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident

from .models import WhatsAppOrder

logger = logging.getLogger(__name__)


@receiver(post_save, sender=WhatsAppOrder)
def handle_new_whatsapp_order(
    sender: Any, instance: WhatsAppOrder, created: bool, **kwargs: Any
) -> None:
    if not created:
        return

    user = getattr(instance, "created_by", None)

    # ✅ 1. تنبيه الذكاء الاصطناعي
    try:
        AIDecisionAlert.objects.create(
            section="whatsapp_bot",
            alert_type="طلب جديد عبر واتساب",
            message=(
                f"📩 طلب واتساب من العميل: {getattr(instance, 'client_name', '-')}"
                f" - المنتج: {getattr(instance, 'product_requested', '-')}"
            ),
            level="info",
        )
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Failed to create AIDecisionAlert for WhatsAppOrder %s: %s",
            instance.pk,
            exc,
        )

    # ✅ 2. تسجيل مخاطرة ذكية عند الشك في الطلب (مثال: كمية غير طبيعية أو عميل غير نشط)
    try:
        if (
            getattr(instance, "quantity", 0) > 100
            or getattr(instance, "status", "") == "معلق"
        ):
            RiskIncident.objects.create(
                user=user,
                category="WhatsApp",
                event_type="طلب غير معتاد",
                risk_level="MEDIUM",
                notes=(
                    f"طلب بكمية كبيرة أو في حالة غير معتادة: "
                    f"{getattr(instance, 'quantity', 0)} وحدة من {getattr(instance, 'product_requested', '-')}"
                ),
            )
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Failed to create RiskIncident for WhatsAppOrder %s: %s", instance.pk, exc
        )
