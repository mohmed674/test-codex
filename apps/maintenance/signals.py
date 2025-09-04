# apps/maintenance/signals.py
from __future__ import annotations

import importlib
import logging
from typing import Any, Optional

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.maintenance.models import MaintenanceLog
from apps.production.models import ProductionStage

logger = logging.getLogger(__name__)

# ----------------------------------------------------
# نماذج من تطبيقات أخرى (تحميل اختياري لتفادي الأعطال)
# ----------------------------------------------------
try:
    _ai = importlib.import_module("apps.ai_decision.models")
    AIDecisionAlert: Optional[Any] = getattr(_ai, "AIDecisionAlert", None)
except Exception as exc:  # noqa: BLE001
    logger.debug("AI decision models not available: %s", exc)
    AIDecisionAlert = None

try:
    _mon = importlib.import_module("apps.internal_monitoring.models")
    RiskIncident: Optional[Any] = getattr(_mon, "RiskIncident", None)
except Exception as exc:  # noqa: BLE001
    logger.debug("Internal monitoring models not available: %s", exc)
    RiskIncident = None


# ✅ تسجيل استهلاك وتشغيل الماكينات
@receiver(post_save, sender=ProductionStage)
def log_machine_usage_on_stage_completion(
    sender: Any, instance: ProductionStage, created: bool, **kwargs: Any
) -> None:
    if created or getattr(instance, "status", None) != "completed":
        return

    machine = getattr(instance, "machine", None)
    if machine is None:
        return

    # حساب مدة التشغيل بالساعات
    try:
        start_time = getattr(instance, "start_time", None)
        end_time = getattr(instance, "end_time", None)
        if start_time and end_time:
            duration = (end_time - start_time).total_seconds() / 3600.0
        else:
            duration = 0.0
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to calculate machine usage duration: %s", exc)
        duration = 0.0

    # ✅ إنشاء سجل صيانة بالتشغيل
    try:
        MaintenanceLog.objects.create(
            machine=machine,
            issue=_("تشغيل لمدة {hours} ساعة").format(hours=round(duration, 2)),
            date_reported=timezone.now(),
            status=_("تم التشغيل"),
            notes=_("تم تشغيل {machine} خلال مرحلة {stage}").format(
                machine=getattr(machine, "name", ""),
                stage=getattr(instance, "stage_name", ""),
            ),
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to create MaintenanceLog (usage): %s", exc)

    # ✅ تحديث ساعات التشغيل الكلية
    try:
        machine.operating_hours = (
            getattr(machine, "operating_hours", 0) or 0
        ) + duration
        machine.last_used_at = timezone.now()
        machine.save(update_fields=["operating_hours", "last_used_at"])
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to update machine operating hours: %s", exc)

    # ⏳ تنبيه إذا تجاوزت ساعات التشغيل حد الصيانة
    if getattr(machine, "operating_hours", 0) >= getattr(
        machine, "maintenance_threshold", float("inf")
    ):
        try:
            MaintenanceLog.objects.create(
                machine=machine,
                issue=_("⚠️ تنبيه: الماكينة تجاوزت حد التشغيل المسموح به"),
                date_reported=timezone.now(),
                status=_("تنبيه"),
                notes=_("تجاوز ساعات التشغيل دون صيانة دورية"),
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to create MaintenanceLog (threshold): %s", exc)

        if AIDecisionAlert is not None:
            try:
                AIDecisionAlert.objects.create(
                    section="maintenance",
                    alert_type=_("صيانة دورية متأخرة"),
                    message=_(
                        "الماكينة {name} تجاوزت حد التشغيل ({hours} ساعة)"
                    ).format(
                        name=getattr(machine, "name", ""),
                        hours=round(getattr(machine, "operating_hours", 0), 2),
                    ),
                    level="warning",
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to create AIDecisionAlert: %s", exc)

        if RiskIncident is not None:
            try:
                RiskIncident.objects.create(
                    user=None,
                    category="System",
                    event_type=_("تجاوز صيانة دورية"),
                    risk_level="MEDIUM",
                    notes=_(
                        "الماكينة {name} تجاوزت حد التشغيل المسموح ({thr} ساعة)"
                    ).format(
                        name=getattr(machine, "name", ""),
                        thr=getattr(machine, "maintenance_threshold", 0),
                    ),
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to create RiskIncident: %s", exc)
