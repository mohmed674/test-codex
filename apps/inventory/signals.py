from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal

# ✅ استيراد النماذج
from .models import InventoryAuditItem, InventoryDiscrepancyInvestigation, InventoryTransaction
from apps.accounting.models import JournalEntry
from apps.ai_decision.models import AIDecisionAlert, AIDecisionLog
from apps.internal_monitoring.models import RiskIncident


# ====================================================
# 🔍 1. تنبيه عند فرق كبير في الجرد الفعلي
# ====================================================
@receiver(post_save, sender=InventoryAuditItem)
def check_discrepancy(sender, instance, created, **kwargs):
    if abs(instance.difference) > 10:  # فرق أكبر من 10 وحدات = خطر
        InventoryDiscrepancyInvestigation.objects.get_or_create(audit_item=instance)
        AIDecisionLog.objects.create(
            source="inventory",
            message=f"فرق كبير في الجرد لصنف {instance.product.name} = {instance.difference}",
            action_suggestion="فتح تحقيق داخلي"
        )


# ====================================================
# 📊 2. قيد محاسبي تلقائي + تنبيه عند انخفاض المخزون
# ====================================================
@receiver(post_save, sender=InventoryTransaction)
def handle_inventory_transaction(sender, instance, created, **kwargs):
    if not created:
        return

    item = instance.item
    quantity = Decimal(instance.quantity or 0)
    unit_cost = Decimal(getattr(item, 'unit_cost', 0))  # تأكد من وجود unit_cost
    amount = unit_cost * abs(quantity)

    if amount == 0:
        return

    # ✅ إنشاء قيد محاسبي حسب نوع الحركة
    if instance.transaction_type == 'IN':
        JournalEntry.objects.create(
            description=f"📦 إضافة للمخزون: {item.name}",
            debit_account="المخزون",
            credit_account="الموردين",
            amount=amount,
            entry_date=timezone.now()
        )
    elif instance.transaction_type == 'OUT':
        JournalEntry.objects.create(
            description=f"🚚 سحب من المخزون: {item.name}",
            debit_account="تكلفة إنتاج",
            credit_account="المخزون",
            amount=amount,
            entry_date=timezone.now()
        )

    # ✅ تنبيه AI عند انخفاض المخزون
    if item.quantity < item.minimum_threshold:
        AIDecisionAlert.objects.create(
            section="inventory",
            alert_type="🚨 مخزون منخفض",
            message=f"⚠️ الكمية المتبقية من {item.name} ({item.quantity}) أقل من الحد الأدنى المحدد ({item.minimum_threshold})",
            level="critical"
        )

        # ✅ تسجيل خطر محتمل في نظام المراقبة
        RiskIncident.objects.create(
            user=None,
            category="Stock",
            event_type="مخزون أقل من الحد الأدنى",
            risk_level="HIGH",
            notes=f"تم رصد كمية منخفضة من المنتج {item.name} بعد حركة {instance.transaction_type}"
        )
