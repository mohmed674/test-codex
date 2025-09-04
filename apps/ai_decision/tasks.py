# ai_decision/tasks.py
from __future__ import annotations

from decimal import Decimal
from typing import Dict, Iterable

from celery import shared_task
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.ai_decision.models import AIDecisionAlert
from apps.products.models import FinishedProduct
from apps.sales.models import SaleItem


def _window_start(now, mode: str) -> timezone.datetime:
    if mode == "daily":
        return now - timezone.timedelta(days=1)
    if mode == "weekly":
        return now - timezone.timedelta(days=7)
    if mode == "monthly":
        return now - timezone.timedelta(days=30)
    # fallback
    return now - timezone.timedelta(days=1)


def _to_decimal(val) -> Decimal:
    if isinstance(val, Decimal):
        return val
    try:
        return Decimal(str(val or 0))
    except Exception:
        return Decimal("0")


def _build_unit_cost_map(product_ids: Iterable[int]) -> Dict[int, Decimal]:
    """
    Return a map: product_id -> unit_cost (prefer production_cost, else cost_price).
    """
    unit_cost_by_id: Dict[int, Decimal] = {}
    if not product_ids:
        return unit_cost_by_id

    rows = FinishedProduct.objects.filter(id__in=list(product_ids)).values(
        "id", "production_cost", "cost_price"
    )
    for r in rows:
        pc = _to_decimal(r.get("production_cost"))
        cp = _to_decimal(r.get("cost_price"))
        unit_cost_by_id[int(r["id"])] = pc if pc > 0 else cp
    return unit_cost_by_id


@shared_task
def analyze_product_sales(mode: str = "daily") -> Dict[str, int]:
    """
    Aggregate sales in a time window and raise AI decision alerts.

    - Window: daily/weekly/monthly (default daily).
    - Aggregation: per product (quantity + revenue).
    - Profit: revenue - (unit_cost * quantity).
    - Emits:
        * low demand (qty < 3)
        * negative profit (profit < 0)
    Returns a summary counts dict.
    """
    now = timezone.now()
    since = _window_start(now, mode)

    # بنود المبيعات المرتبطة بفواتير في النافذة
    sales = SaleItem.objects.filter(invoice__date__gte=since)

    # إجمالي الكمية والإيرادات لكل منتج
    product_data = list(
        sales.values("product__id", "product__name").annotate(
            total_sales=Sum("quantity"),
            total_revenue=Sum(F("quantity") * F("unit_price")),
        )
    )

    product_ids = [
        int(d["product__id"]) for d in product_data if d.get("product__id") is not None
    ]
    unit_cost_map = _build_unit_cost_map(product_ids)

    created_low_demand = 0
    created_loss = 0

    for data in product_data:
        pid = int(data["product__id"])
        name = data["product__name"] or f"#{pid}"
        total_sales = int(data.get("total_sales") or 0)
        total_revenue = _to_decimal(data.get("total_revenue"))

        unit_cost = unit_cost_map.get(pid, Decimal("0"))
        total_cost = unit_cost * Decimal(total_sales)
        profit = total_revenue - total_cost

        if total_sales < 3:
            AIDecisionAlert.objects.create(
                section="sales",
                alert_type="منتج راكد",
                message=_("المنتج '{name}' لم يحقق مبيعات ({mode})").format(
                    name=name, mode=mode
                ),
                level="warning",
            )
            created_low_demand += 1

        if profit < 0:
            AIDecisionAlert.objects.create(
                section="sales",
                alert_type="خسارة في منتج",
                message=_("المنتج '{name}' يحقق خسارة ({mode})").format(
                    name=name, mode=mode
                ),
                level="danger",
            )
            created_loss += 1

    return {
        "analyzed": len(product_data),
        "low_demand": created_low_demand,
        "loss": created_loss,
        "mode": {"daily": 1, "weekly": 7, "monthly": 30}.get(mode, 1),
    }
