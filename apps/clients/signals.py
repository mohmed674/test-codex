from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import F
from datetime import date

from apps.sales.models import SaleInvoice
from .models import Customer  # الموديل الأصلي (مش Client البروكسي)

# نخلي تسجيل المخاطر اختياري عشان ما يكسرش لو التطبيق مش موجود
try:
    from apps.internal_monitoring.models import RiskIncident
except Exception:
    RiskIncident = None


@receiver(post_save, sender=SaleInvoice)
def update_client_data(sender, instance, created, **kwargs):
    if not created:
        return

    # لازم يكون عند الفاتورة عميل مرتبط
    customer = getattr(instance, "client", None)
    if customer is None:
        return

    amount = instance.total_amount or 0
    inc_points = int(amount // 100)

    # تحديث ذَرّي آمن (مايتأثرش لو في حفظات متزامنة)
    Customer.objects.filter(pk=customer.pk).update(
        total_purchases=F("total_purchases") + amount,
        points=F("points") + inc_points,
        last_purchase_date=timezone.localdate(),
    )

    # لو المبلغ كبير نسجل مخاطرة (إن وجد الموديل)
    if RiskIncident and amount >= 10000:
        risk_level = "MEDIUM" if amount < 50000 else "HIGH"
        user = getattr(instance, "created_by", None)
        client_name = getattr(getattr(customer, "partner", None), "name", str(customer.pk))
        try:
            RiskIncident.objects.create(
                user=user,
                category="Sales",
                event_type="عملية بيع بمبلغ كبير",
                risk_level=risk_level,
                notes=f"تم تسجيل فاتورة بمبلغ {amount} للعميل {client_name} بتاريخ {timezone.localdate()}",
            )
        except Exception:
            pass
