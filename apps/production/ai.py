# ERP_CORE/production/ai.py
from __future__ import annotations

from typing import Any

from apps.ai_decision.models import AIDecisionAlert

from .models import ProductionOrder


def detect_delayed_orders() -> None:
    """
    Detect production orders whose deadline has passed and are not completed,
    then create AI decision alerts. Uses getattr for safety since 'deadline'
    may not be defined in all schemas.
    """
    from django.utils.timezone import now

    today = now().date()
    orders = ProductionOrder.objects.all()

    for order in orders:
        deadline: Any = getattr(order, "deadline", None)
        if deadline and hasattr(deadline, "isoformat"):
            if (
                deadline < today
                and str(getattr(order, "status", "")).lower() != "completed"
            ):
                AIDecisionAlert.objects.create(
                    section="production",
                    alert_type="تأخير في أمر إنتاج",
                    level="high",
                    message=f"تأخر في أمر التشغيل {order.order_number} عن موعده.",
                )
