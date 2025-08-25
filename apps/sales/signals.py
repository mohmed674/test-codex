# ERP_CORE/sales/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SaleInvoice
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident
from django.contrib.auth.models import User


@receiver(post_save, sender=SaleInvoice)
def handle_sale_invoice(sender, instance, created, **kwargs):
    user = instance.created_by if hasattr(instance, 'created_by') else User.objects.filter(is_superuser=True).first()

    # ✅ 1. تنبيه AI عند فاتورة كبيرة
    if instance.total_amount >= 10000:
        AIDecisionAlert.objects.create(
            section='sales',
            alert_type='فاتورة مبيعات كبيرة',
            message=f"فاتورة رقم {instance.id} بمبلغ كبير: {instance.total_amount}",
            level='info'
        )

    # ✅ 2. مراقبة المخالفات الذكية: إجمالي بالسالب
    if instance.total_amount < 0:
        RiskIncident.objects.create(
            user=user,
            category='Sales',
            event_type='إجمالي فاتورة بالسالب',
            risk_level='HIGH',
            notes=f'تم إدخال فاتورة رقم {instance.id} بمبلغ سالب = {instance.total_amount}'
        )

    # ✅ 3. مراقبة الخصومات المفرطة
    if instance.discount_amount and instance.discount_amount > instance.total_amount * 0.5:
        RiskIncident.objects.create(
            user=user,
            category='Sales',
            event_type='خصم مفرط',
            risk_level='MEDIUM',
            notes=f'الخصم على الفاتورة رقم {instance.id} تجاوز 50% من القيمة الإجمالية'
        )
