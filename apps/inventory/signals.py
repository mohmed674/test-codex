# apps/inventory/signals.py
from __future__ import annotations

import importlib
import logging
from decimal import Decimal
from typing import Any, Optional

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# ✅ نماذج داخل التطبيق
from .models import InventoryAuditItem, InventoryDiscrepancyInvestigation

logger = logging.getLogger(__name__)

# ----------------------------------------------------
# نماذج من تطبيقات أخرى (اختيارية لتفادي الأعطال مع mypy)
# ----------------------------------------------------
try:
    _acc = importlib.import_module("apps.accounting.models")
    JournalEntry: Optional[Any] = getattr(_acc, "JournalEntry", None)
except Exception as exc:  # noqa: BLE001
    logger.debug("Accounting models not available: %s", exc)
    JournalEntry = None

try:
    _ai = importlib.import_module("apps.ai_decision.models")
    AIDecisionAlert: Optional[Any] = getattr(_ai, "AIDecisionAlert", None)
    AIDecisionLog: Optional[Any] = getattr(_ai, "AIDecisionLog", None)
except Exception as exc:  # noqa: BLE001
    logger.debug("AI decision models not available: %s", exc)
    AIDecisionAlert = None
    AIDecisionLog = None

try:
    _mon = importlib.import_module("apps.internal_monitoring.models")
    RiskIncident: Optional[Any] = getattr(_mon, "RiskIncident", None)
except Exception as exc:  # noqa: BLE001
    logger.debug("Internal monitoring models not available: %s", exc)
    RiskIncident = None

# لاحظ: mypy اشتكى أن InventoryTransaction غير موجود؛
# لذلك نحمّله ديناميكيًا ونسجل الإشارة برمجيًا لاحقًا.
try:
    _inv_models = importlib.import_module("apps.inventory.models")
    InventoryTransaction: Optional[Any] = getattr(
        _inv_models, "InventoryTransaction", None
    )
except Exception as exc:  # noqa: BLE001
    logger.debug("Inventory models not available: %s", exc)
    InventoryTransaction = None


# ====================================================
# 🔍 1) تنبيه عند فرق كبير في الجرد الفعلي
# ====================================================
@receiver(post_save, sender=InventoryAuditItem)
def check_discrepancy(
    sender: Any, instance: InventoryAuditItem, created: bool, **kwargs: Any
) -> None:
    try:
        difference = Decimal(getattr(instance, "difference", 0) or 0)
    except Exception:  # noqa: BLE001
        difference = Decimal(0)

    if abs(difference) > Decimal(10):
        InventoryDiscrepancyInvestigation.objects.get_or_create(audit_item=instance)
        if AIDecisionLog is not None:
            try:
                prod_name = getattr(getattr(instance, "product", None), "name", "")
                AIDecisionLog.objects.create(
                    source="inventory",
                    message=_("فرق كبير في الجرد لصنف {name} = {diff}").format(
                        name=prod_name,
                        diff=str(difference),
                    ),
                    action_suggestion=_("فتح تحقيق داخلي"),
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to create AIDecisionLog: %s", exc)


# ====================================================
# 📊 2) قيد محاسبي تلقائي + تنبيه عند انخفاض المخزون
#    (تسجيل الإشارة ديناميكيًا لتفادي مشاكل mypy)
# ====================================================
def handle_inventory_transaction(
    sender: Any, instance: Any, created: bool, **kwargs: Any
) -> None:
    if not created:
        return

    item = getattr(instance, "item", None)
    if item is None:
        return

    quantity = Decimal(getattr(instance, "quantity", 0) or 0)
    unit_cost = Decimal(getattr(item, "unit_cost", 0) or 0)
    amount = unit_cost * abs(quantity)

    if amount == 0:
        return

    # ✅ إنشاء قيد محاسبي حسب نوع الحركة
    tx_type = getattr(instance, "transaction_type", "")
    item_name = getattr(item, "name", "")

    if JournalEntry is not None:
        try:
            if tx_type == "IN":
                JournalEntry.objects.create(
                    description=_("إضافة للمخزون: {name}").format(name=item_name),
                    debit_account=_("المخزون"),
                    credit_account=_("الموردين"),
                    amount=amount,
                    entry_date=timezone.now(),
                )
            elif tx_type == "OUT":
                JournalEntry.objects.create(
                    description=_("سحب من المخزون: {name}").format(name=item_name),
                    debit_account=_("تكلفة إنتاج"),
                    credit_account=_("المخزون"),
                    amount=amount,
                    entry_date=timezone.now(),
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to create JournalEntry: %s", exc)
    else:
        logger.warning("JournalEntry not available; skipped accounting entry.")

    # ✅ تنبيه AI عند انخفاض المخزون + تسجيل خطر
    qty = Decimal(getattr(item, "quantity", 0) or 0)
    min_thr = Decimal(getattr(item, "minimum_threshold", 0) or 0)

    if qty < min_thr:
        if AIDecisionAlert is not None:
            try:
                AIDecisionAlert.objects.create(
                    section="inventory",
                    alert_type=_("مخزون منخفض"),
                    message=_(
                        "الكمية المتبقية من {name} ({qty}) أقل من الحد الأدنى ({min})"
                    ).format(name=item_name, qty=str(qty), min=str(min_thr)),
                    level="critical",
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to create AIDecisionAlert: %s", exc)

        if RiskIncident is not None:
            try:
                RiskIncident.objects.create(
                    user=None,
                    category="Stock",
                    event_type=_("مخزون أقل من الحد الأدنى"),
                    risk_level="HIGH",
                    notes=_("تم رصد كمية منخفضة من المنتج {name} بعد حركة {tx}").format(
                        name=item_name, tx=tx_type
                    ),
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to create RiskIncident: %s", exc)


# ربط الإشارة ديناميكيًا لتفادي خطأ mypy عندما يكون الموديل غير معروف
if InventoryTransaction is not None:
    post_save.connect(
        handle_inventory_transaction,
        sender=InventoryTransaction,  # type: ignore[arg-type]
        dispatch_uid="inventory_handle_inventory_transaction",
    )
