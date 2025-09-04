from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from typing import DefaultDict, Dict, TypedDict

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.ai_decision.models import AIDecisionAlert
from apps.sales.models import SaleItem


class ProductAgg(TypedDict):
    name: str
    total_qty: int
    total_profit: float


def _default_agg() -> ProductAgg:
    return {"name": "", "total_qty": 0, "total_profit": 0.0}


def analyze_sales_profitability() -> Dict[str, int]:
    """
    Analyze recent sales profitability and emit AIDecisionAlert entries.

    - Aggregates last N days (default 30) from SaleItem to avoid N+1.
    - Tracks per-product totals: quantity and profit.
    - Emits alerts for low demand, low profit, and top performers.

    Returns:
        Summary dict with counts per alert category.
    """
    days = getattr(settings, "AI_DECISION_ANALYSIS_WINDOW_DAYS", 30)

    low_demand_threshold = getattr(settings, "AI_DECISION_LOW_DEMAND_THRESHOLD", 3)
    low_profit_threshold = getattr(settings, "AI_DECISION_LOW_PROFIT_THRESHOLD", 100.0)
    high_qty_threshold = getattr(settings, "AI_DECISION_HIGH_QTY_THRESHOLD", 10)
    high_profit_threshold = getattr(
        settings, "AI_DECISION_HIGH_PROFIT_THRESHOLD", 1000.0
    )

    start_date = timezone.now().date() - timedelta(days=days)

    # اجلب العناصر مع product و sale لتفادي N+1
    items = SaleItem.objects.select_related("product", "sale").filter(
        sale__date__gte=start_date
    )

    stats: DefaultDict[int, ProductAgg] = defaultdict(_default_agg)

    for item in items:
        product = item.product

        # PK آمنة بدلاً من .id مع تحقّق وتحويل إلى int
        pk = getattr(product, "pk", None)
        if pk is None:
            # منتج غير محفوظ/غير صالح؛ نتخطّى السجل بحذر
            continue
        pid = int(pk)

        production_cost = getattr(product, "production_cost", 0.0) or 0.0
        unit_price = getattr(item, "unit_price", 0.0) or 0.0
        qty = getattr(item, "quantity", 0) or 0

        profit = (unit_price - production_cost) * qty

        rec = stats[pid]
        rec["name"] = getattr(product, "name", f"#{pid}")
        rec["total_qty"] += int(qty)
        rec["total_profit"] += float(profit)

    created_low_demand = 0
    created_low_profit = 0
    created_top_perf = 0

    for _pid, rec in stats.items():
        name = rec["name"]
        qty = rec["total_qty"]
        profit = rec["total_profit"]

        if qty <= low_demand_threshold:
            AIDecisionAlert.objects.create(
                section="sales",
                alert_type="low_demand",
                message=_(
                    "المنتج '{name}' يعتبر راكد (الكمية المباعة = {qty})."
                ).format(name=name, qty=qty),
                level="warning",
            )
            created_low_demand += 1

        if profit < low_profit_threshold:
            AIDecisionAlert.objects.create(
                section="sales",
                alert_type="low_profit",
                message=_("المنتج '{name}' حقق ربحًا منخفضًا ({profit:.2f}).").format(
                    name=name, profit=profit
                ),
                level="info",
            )
            created_low_profit += 1

        if qty > high_qty_threshold and profit > high_profit_threshold:
            AIDecisionAlert.objects.create(
                section="sales",
                alert_type="top_performer",
                message=_(
                    "المنتج '{name}' عالي الربحية ({profit:.2f}) "
                    "ومطلوب بشدة (الكمية = {qty})."
                ).format(name=name, profit=profit, qty=qty),
                level="success",
            )
            created_top_perf += 1

    return {
        "low_demand": created_low_demand,
        "low_profit": created_low_profit,
        "top_performer": created_top_perf,
        "analyzed_products": len(stats),
        "window_days": days,
    }
