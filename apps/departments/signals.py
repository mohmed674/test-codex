# apps/departments/signals.py
from __future__ import annotations

import inspect
from typing import Any

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timezone import now

from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import ReportLog, RiskIncident
from core.utils import log_user_action

from .models import Department


def _safe_log_user_action(user: Any, action: str, **extra: Any) -> None:
    """
    Call core.utils.log_user_action with only the parameters it accepts.
    This keeps signals compatible across different implementations.
    """
    try:
        sig = inspect.signature(log_user_action)
        payload = {"user": user, "action": action, **extra}
        accepted = {k: v for k, v in payload.items() if k in sig.parameters}
        log_user_action(**accepted)  # type: ignore[misc]
    except Exception:
        # Swallow any logging error; signals must not crash saves/deletes.
        return


@receiver(post_save, sender=Department)
def notify_ai_on_department_change(
    sender, instance: Department, created: bool, **kwargs: Any
) -> None:
    AIDecisionAlert.objects.create(
        section="departments",
        alert_type="إنشاء قسم جديد" if created else "تحديث قسم",
        message=f"تم {'إضافة' if created else 'تحديث'} قسم: {instance.name}",
        level="info",
        timestamp=now(),
    )

    RiskIncident.objects.create(
        user=None,
        category="System",
        event_type="إنشاء قسم جديد" if created else "تعديل قسم",
        risk_level="LOW" if created else "MEDIUM",
        notes=f"تم {'إضافة' if created else 'تعديل'} قسم {instance.name} في النظام.",
        reported_at=now(),
    )

    ReportLog.objects.create(
        model="Department",
        action="Create" if created else "Update",
        ref=str(instance.pk),
        notes=f"{'أُنشئ' if created else 'تحديث'} قسم: {instance.name}",
        timestamp=now(),
    )

    # تتبع المستخدم إن توفّر توقيع الدالة
    _safe_log_user_action(
        user=kwargs.get("user", None),
        action="create" if created else "update",
        model="Department",
        instance_id=instance.pk,
        description=f"{'إضافة' if created else 'تعديل'} قسم {instance.name}",
        timestamp=str(now()),
    )


@receiver(pre_delete, sender=Department)
def notify_on_department_deletion(sender, instance: Department, **kwargs: Any) -> None:
    AIDecisionAlert.objects.create(
        section="departments",
        alert_type="حذف قسم",
        message=f"🚫 تم حذف القسم: {instance.name}",
        level="warning",
        timestamp=now(),
    )

    RiskIncident.objects.create(
        user=None,
        category="System",
        event_type="حذف قسم",
        risk_level="HIGH",
        notes=f"⚠️ حذف القسم: {instance.name} من النظام.",
        reported_at=now(),
    )

    ReportLog.objects.create(
        model="Department",
        action="Delete",
        ref=str(instance.pk),
        notes=f"🚨 تم حذف قسم: {instance.name}",
        timestamp=now(),
    )

    _safe_log_user_action(
        user=kwargs.get("user", None),
        action="delete",
        model="Department",
        instance_id=instance.pk,
        description=f"حذف قسم {instance.name}",
        timestamp=str(now()),
    )
