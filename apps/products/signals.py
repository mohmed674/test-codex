# ERP_CORE/products/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from apps.accounting.models import JournalEntry
from apps.ai_decision.models import AIDecisionAlert
from django.utils import timezone


@receiver(post_save, sender=Product)
def handle_product_change(sender, instance, created, **kwargs):
    # ✅ إرسال تنبيه للذكاء الاصطناعي عند تعديل السعر
    if not created:
        AIDecisionAlert.objects.create(
            section="products",
            alert_type="تحديث سعر المنتج",
            message=f"تم تحديث سعر المنتج {instance.name} إلى {instance.retail_price}",
            level="info"
        )

    # ✅ تسجيل قيد محاسبي عند إدخال منتج جديد بتكلفة
    if created and instance.cost > 0:
        JournalEntry.objects.create(
            description=f"إدخال منتج {instance.name} بتكلفة {instance.cost}",
            debit_account="المخزون",
            credit_account="رأس المال",
            amount=instance.cost,
            entry_date=timezone.now()
        )
