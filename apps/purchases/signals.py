# ERP_CORE/purchases/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident

from .models import PurchaseOrder, PurchaseRequest


@receiver(post_save, sender=PurchaseRequest)
def alert_on_critical_request(sender, instance, created, **kwargs):
    if created and instance.purpose and "عاجل" in instance.purpose:
        AIDecisionAlert.objects.create(
            section="purchases",
            alert_type="طلب عاجل",
            message=f"🛑 طلب عاجل من قسم {instance.department.name}",
            level="warning",
        )


@receiver(post_save, sender=PurchaseOrder)
def alert_on_high_value_order(sender, instance, created, **kwargs):
    if created and instance.total_amount > 100000:
        AIDecisionAlert.objects.create(
            section="purchases",
            alert_type="أمر شراء مرتفع القيمة",
            message=f"💸 أمر شراء كبير من المورد {instance.supplier_name} بمبلغ {instance.total_amount}",
            level="critical",
        )

        RiskIncident.objects.create(
            user=None,
            category="Finance",
            event_type="أمر شراء كبير",
            risk_level="HIGH",
            notes=f"مبلغ الأمر: {instance.total_amount}",
        )
