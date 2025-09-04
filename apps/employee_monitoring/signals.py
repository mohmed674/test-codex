# apps/employee_monitoring/signals.py
import importlib
import logging
from typing import Any, Optional

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .models import MonitoringRecord

logger = logging.getLogger(__name__)

# Optional imports to avoid hard dependencies and keep mypy happy
try:
    _ai_models = importlib.import_module("apps.ai_decision.models")
    AIDecisionAlert: Optional[Any] = getattr(_ai_models, "AIDecisionAlert", None)
except Exception as exc:  # ImportError or any app-loading issue
    logger.debug("apps.ai_decision.models not available: %s", exc)
    AIDecisionAlert = None

try:
    _internal_mon = importlib.import_module("apps.internal_monitoring.models")
    RiskIncident: Optional[Any] = getattr(_internal_mon, "RiskIncident", None)
except Exception as exc:
    logger.debug("apps.internal_monitoring.models not available: %s", exc)
    RiskIncident = None


@receiver(post_save, sender=MonitoringRecord)
def alert_ai_on_monitor_log(
    sender: Any, instance: MonitoringRecord, created: bool, **kwargs: Any
) -> None:
    # Trigger only on error entries
    if getattr(instance, "entry_status", None) != "error":
        return

    # AI alert (optional)
    if AIDecisionAlert is not None:
        try:
            AIDecisionAlert.objects.create(
                section="monitoring",
                alert_type=_("فشل دخول"),
                message=_("فشل دخول {user} في {section}").format(
                    user=str(getattr(instance, "user", "")),
                    section=str(getattr(instance, "section", "")),
                ),
                level="high",
            )
        except Exception as exc:
            logger.error("Failed to create AIDecisionAlert: %s", exc)

    # Risk logging (optional)
    if RiskIncident is not None:
        try:
            RiskIncident.objects.create(
                user=getattr(instance, "user", None),
                category="System",
                event_type=_("محاولة دخول غير ناجحة"),
                risk_level="HIGH",
                notes=_("تم رصد محاولة دخول فاشلة في القسم: {section}").format(
                    section=str(getattr(instance, "section", "")),
                ),
            )
        except Exception as exc:
            logger.error("Failed to create RiskIncident: %s", exc)
