# mrp/tasks.py
from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict, List

from django.utils import timezone

from .models import DEC_ZERO, MaterialPlanning, PlanningStatus, PlanningType

logger = logging.getLogger(__name__)


def auto_generate_planning(upcoming: List[Dict[str, Any]] | None = None) -> None:
    """
    توليد خطط مواد مبدئية (MaterialPlanning) من توقعات الإنتاج أو مدخلات خارجية.
    'upcoming' يمكن أن يكون قائمة قواميس تحتوي على مفاتيح:
      - product: كائن Product أو مفتاحه
      - planned_quantity: الكمية المخططة
      - required_date: تاريخ الحاجة (date)
      - warehouse: اسم/رمز المخزن
    """
    upcoming = upcoming or []
    for item in upcoming:
        try:
            MaterialPlanning.objects.create(
                product=item.get("product"),
                planned_quantity=item.get("planned_quantity", DEC_ZERO),
                uom_code=item.get("uom_code", ""),
                required_date=item.get("required_date", date.today()),
                warehouse=item.get("warehouse", ""),
                planning_type=item.get("planning_type", PlanningType.MRP),
                status=PlanningStatus.DRAFT,
                priority=item.get("priority", 2),
                version=1,
                demand_source=item.get("demand_source", "MANUAL"),
                demand_ref=item.get("demand_ref", ""),
                auto_generated=True,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to auto-generate planning for item=%s: %s", item, exc)
