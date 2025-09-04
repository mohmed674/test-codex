# apps/production/signals.py
from __future__ import annotations

import importlib
import logging
from decimal import Decimal
from typing import Any, Optional, cast

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import MaterialConsumption, ProductionOrder

logger = logging.getLogger(__name__)

# --- Optional, mypy-safe dynamic imports for cross-app models ---
try:
    _acc = importlib.import_module("apps.accounting.models")
    JournalEntry: Optional[Any] = getattr(_acc, "JournalEntry", None)
except Exception as exc:  # noqa: BLE001
    logger.debug("Accounting models not available: %s", exc)
    JournalEntry = None

try:
    _ai = importlib.import_module("apps.ai_decision.models")
    # Support both names if project uses AIDecisionLog instead of DecisionLog
    DecisionLog: Optional[Any] = getattr(
        _ai, "DecisionLog", getattr(_ai, "AIDecisionLog", None)
    )
except Exception as exc:  # noqa: BLE001
    logger.debug("AI decision models not available: %s", exc)
    DecisionLog = None

try:
    _eval = importlib.import_module("apps.evaluation.models")
    Evaluation: Optional[Any] = getattr(_eval, "Evaluation", None)
except Exception as exc:  # noqa: BLE001
    logger.debug("Evaluation models not available: %s", exc)
    Evaluation = None

try:
    _inv = importlib.import_module("apps.inventory.models")
    InventoryTransaction: Optional[Any] = getattr(_inv, "InventoryTransaction", None)
except Exception as exc:  # noqa: BLE001
    logger.debug("Inventory models not available: %s", exc)
    InventoryTransaction = None

try:
    _mnt = importlib.import_module("apps.maintenance.models")
    MachineUsageLog: Optional[Any] = getattr(_mnt, "MachineUsageLog", None)
except Exception as exc:  # noqa: BLE001
    logger.debug("Maintenance models not available: %s", exc)
    MachineUsageLog = None

try:
    _pay = importlib.import_module("apps.payroll.models")
    PieceRateRecord: Optional[Any] = getattr(_pay, "PieceRateRecord", None)
except Exception as exc:  # noqa: BLE001
    logger.debug("Payroll models not available: %s", exc)
    PieceRateRecord = None
# ----------------------------------------------------------------

# Attribute names (avoid B009 by not using string literals inline)
ATTR_REQUIRED_MATERIALS = "required_materials"
ATTR_ASSIGNED_TO = "assigned_to"
ATTR_USED_MACHINES = "used_machines"
ATTR_ESTIMATED_HOURS = "estimated_hours"
ATTR_ITEM = "item"
ATTR_QTY_REQUIRED = "quantity_required"
ATTR_UNIT_COST = "unit_cost"
ATTR_JOB_TITLE = "job_title"
ATTR_DEFAULT_PIECE_RATE = "default_piece_rate"


@receiver(post_save, sender=ProductionOrder)
def handle_production_order_created(
    sender: Any, instance: ProductionOrder, created: bool, **kwargs: Any
) -> None:
    if not created:
        return

    # ✅ 1) سحب خامات من المخزون + تسجيل استهلاك
    raw_rel = getattr(instance, ATTR_REQUIRED_MATERIALS, None)
    raw_materials = list(cast(Any, raw_rel).all()) if raw_rel is not None else []

    for material in raw_materials:
        # Inventory move
        if InventoryTransaction is not None:
            try:
                item = getattr(material, ATTR_ITEM, None)
                qty_required = Decimal(getattr(material, ATTR_QTY_REQUIRED, 0) or 0)
                InventoryTransaction.objects.create(
                    item=item,
                    quantity=-qty_required,
                    transaction_type="OUT",
                    related_order=instance,
                    note=_("سحب خامة لأمر إنتاج {num}").format(
                        num=str(instance.order_number)
                    ),
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed InventoryTransaction create: %s", exc)
        else:
            logger.warning("InventoryTransaction not available; skipping stock move.")

        # Material consumption record
        try:
            item = getattr(material, ATTR_ITEM, None)
            item_name = (
                item.name if (item is not None and hasattr(item, "name")) else ""
            )
            item_unit = (
                item.unit if (item is not None and hasattr(item, "unit")) else ""
            )
            qty_used = Decimal(getattr(material, ATTR_QTY_REQUIRED, 0) or 0)
            MaterialConsumption.objects.create(
                order=instance,
                material_name=item_name,
                quantity_used=qty_used,
                unit=item_unit,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed MaterialConsumption create: %s", exc)

    # ✅ 2) قيد تكلفة الخامات في المحاسبة
    def _unit_cost(m: Any) -> Decimal:
        item = getattr(m, ATTR_ITEM, None)
        if item is not None and hasattr(item, ATTR_UNIT_COST):
            val = getattr(item, ATTR_UNIT_COST)
            try:
                return Decimal(val or 0)
            except Exception:  # noqa: BLE001
                return Decimal(0)
        return Decimal(0)

    total_cost = sum(
        _unit_cost(m) * Decimal(getattr(m, ATTR_QTY_REQUIRED, 0) or 0)
        for m in raw_materials
    )

    if total_cost > 0:
        if JournalEntry is not None:
            try:
                JournalEntry.objects.create(
                    description=_("تكلفة خامات أمر إنتاج {num}").format(
                        num=str(instance.order_number)
                    ),
                    debit_account=_("تكلفة إنتاج"),
                    credit_account=_("المخزون"),
                    amount=total_cost,
                    entry_date=timezone.now(),
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed JournalEntry create: %s", exc)
        else:
            logger.warning("JournalEntry not available; skipping accounting entry.")

    # ✅ 3) تسجيل المرتب بنظام القطعة + ✅ 4) تقييم الأداء
    assigned_rel = getattr(instance, ATTR_ASSIGNED_TO, None)
    if assigned_rel is not None and assigned_rel.exists():
        for employee in assigned_rel.all():
            if PieceRateRecord is not None:
                try:
                    job_title = getattr(employee, ATTR_JOB_TITLE, None)
                    rate = (
                        getattr(job_title, ATTR_DEFAULT_PIECE_RATE)
                        if (
                            job_title is not None
                            and hasattr(job_title, ATTR_DEFAULT_PIECE_RATE)
                        )
                        else 0
                    )
                    PieceRateRecord.objects.create(
                        employee=employee,
                        production_order=instance,
                        pieces_count=0,
                        rate_per_piece=rate,
                        date=timezone.now(),
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.error("Failed PieceRateRecord create: %s", exc)
            else:
                logger.warning("PieceRateRecord not available; skipped piece rate.")

            if Evaluation is not None:
                try:
                    Evaluation.objects.create(
                        employee=employee,
                        score=5,
                        note=_("مشاركة في أمر إنتاج {num}").format(
                            num=str(instance.order_number)
                        ),
                        evaluation_date=timezone.now(),
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.error("Failed Evaluation create: %s", exc)
            else:
                logger.warning("Evaluation not available; skipped evaluation record.")

    # ✅ 5) تسجيل استهلاك الماكينات
    used_rel = getattr(instance, ATTR_USED_MACHINES, None)
    if used_rel is not None and MachineUsageLog is not None:
        for machine in used_rel.all():
            try:
                est_hours = Decimal(getattr(instance, ATTR_ESTIMATED_HOURS, 0) or 0)
                MachineUsageLog.objects.create(
                    machine=machine,
                    production_order=instance,
                    usage_hours=est_hours,
                    usage_date=timezone.now(),
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed MachineUsageLog create: %s", exc)
    elif used_rel is not None and MachineUsageLog is None:
        logger.warning("MachineUsageLog not available; skipped machine usage logs.")

    # ✅ 6) تسجيل في نظام الذكاء الاصطناعي للمراجعة
    if DecisionLog is not None:
        try:
            DecisionLog.objects.create(
                related_module=_("الإنتاج"),
                description=_("تم إصدار أمر إنتاج رقم {num}").format(
                    num=str(instance.order_number)
                ),
                created_at=timezone.now(),
                status="pending_analysis",
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed DecisionLog create: %s", exc)
    else:
        logger.warning("DecisionLog/AIDecisionLog not available; skipped AI logging.")
