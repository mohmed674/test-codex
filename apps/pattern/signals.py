# ERP_CORE/pattern/signals.py
from __future__ import annotations

import logging
from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident

from .models import PatternDesign

logger = logging.getLogger(__name__)


@receiver(post_save, sender=PatternDesign)
def notify_ai_and_risk_on_pattern_change(
    sender: Any, instance: PatternDesign, created: bool, **kwargs: Any
) -> None:
    user = getattr(instance, "modified_by", None)
    title = getattr(instance, "title", getattr(instance, "name", "-"))

    # تنبيه الذكاء الاصطناعي
    try:
        AIDecisionAlert.objects.create(
            section="pattern",
            alert_type="تعديل باترون" if not created else "إنشاء باترون جديد",
            message=f"{'تعديل' if not created else 'إضافة'} باترون: {title}",
            level="info" if created else "warning",
        )
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Failed to create AIDecisionAlert for PatternDesign %s: %s",
            getattr(instance, "pk", None),
            exc,
        )

    # تسجيل مخاطرة عند تعديل باترون حرج
    try:
        is_critical = bool(getattr(instance, "is_critical", False))
        if not created and is_critical:
            RiskIncident.objects.create(
                user=user,
                category="Pattern",
                event_type="تعديل باترون حرج",
                risk_level="HIGH",
                notes=f"تم تعديل الباترون الحرج: {title}",
            )
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Failed to create RiskIncident for PatternDesign %s: %s",
            getattr(instance, "pk", None),
            exc,
        )
