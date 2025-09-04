# apps/monitoring/signals.py
from __future__ import annotations

import importlib
import logging
from typing import Any, Optional

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .models import CapturedImage

logger = logging.getLogger(__name__)

# اختياري: فك الارتباط مع التطبيقات الأخرى لتجنب أعطال وقت التحميل
try:
    _ai = importlib.import_module("apps.ai_decision.models")
    AIDecisionAlert: Optional[Any] = getattr(_ai, "AIDecisionAlert", None)
except Exception as exc:  # noqa: BLE001
    logger.debug("AI decision models not available: %s", exc)
    AIDecisionAlert = None

try:
    _alerts = importlib.import_module("apps.internal_monitoring.alerts")
    trigger_risk_alert = getattr(_alerts, "trigger_risk_alert", None)
except Exception as exc:  # noqa: BLE001
    logger.debug("internal_monitoring alerts not available: %s", exc)
    trigger_risk_alert = None


@receiver(post_save, sender=CapturedImage)
def notify_ai_on_capture(
    sender: Any, instance: CapturedImage, created: bool, **kwargs: Any
) -> None:
    if not created:
        return

    ts = getattr(instance, "timestamp", None)
    cam_id = getattr(instance, "camera_id", None)
    cam_user = getattr(instance, "camera_user", None)
    captured_by = getattr(instance, "captured_by", None)

    ts_str = ts.strftime("%Y-%m-%d %H:%M") if ts else ""
    cam_label = cam_id if cam_id else _("غير محددة")

    # تنبيه الذكاء الاصطناعي
    if AIDecisionAlert is not None:
        try:
            AIDecisionAlert.objects.create(
                section="monitoring",
                alert_type=_("التقاط صورة منتج"),
                message=_("تم التقاط صورة بتاريخ {dt} بواسطة الكاميرا {cam}").format(
                    dt=ts_str, cam=cam_label
                ),
                level="info",
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to create AIDecisionAlert: %s", exc)

    # تحذير خارج أوقات العمل
    if ts is not None and (ts.hour < 7 or ts.hour > 19) and trigger_risk_alert:
        try:
            user = captured_by if captured_by else cam_user
            trigger_risk_alert(
                event=_("التقاط صورة خارج أوقات العمل"),
                user=user,
                risk_level="MEDIUM",
                note=_("تم التقاط صورة في الساعة {h}").format(h=ts.strftime("%H:%M")),
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to trigger risk alert: %s", exc)
