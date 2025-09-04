import importlib
import logging
from typing import Any, Optional

from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.sales.models import SaleInvoice

from .models import Customer  # الموديل الأصلي (مش Client البروكسي)

logger = logging.getLogger(__name__)

# Optional import for RiskIncident (keeps mypy happy and avoids hard dependency)
_internal_mon = importlib.import_module("apps.internal_monitoring.models", package=None)
RiskIncidentModel: Optional[Any] = getattr(_internal_mon, "RiskIncident", None)


@receiver(post_save, sender=SaleInvoice)
def update_client_data(
    sender: Any, instance: SaleInvoice, created: bool, **kwargs: Any
) -> None:
    if not created:
        return

    customer = getattr(instance, "client", None)
    if customer is None:
        return

    amount = instance.total_amount or 0
    inc_points = int(amount // 100)

    Customer.objects.filter(pk=customer.pk).update(
        total_purchases=F("total_purchases") + amount,
        points=F("points") + inc_points,
        last_purchase_date=timezone.localdate(),
    )

    if RiskIncidentModel is not None and amount >= 10000:
        risk_level = "MEDIUM" if amount < 50000 else "HIGH"
        user = getattr(instance, "created_by", None)
        partner = getattr(customer, "partner", None)
        client_name = getattr(partner, "name", str(customer.pk))
        try:
            RiskIncidentModel.objects.create(
                user=user,
                category="Sales",
                event_type=_("عملية بيع بمبلغ كبير"),
                risk_level=risk_level,
                notes=_(
                    "تم تسجيل فاتورة بمبلغ {amount} للعميل {client} بتاريخ {date}"
                ).format(amount=amount, client=client_name, date=timezone.localdate()),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to log RiskIncident for high-value sale: %s", exc)
