# ERP_CORE/inventory/management/commands/ai_inventory_analysis.py

from django.core.management.base import BaseCommand
from apps.inventory.models import InventoryItem
from apps.ai_decision.models import AIDecisionAlert
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "تحليل المخزون باستخدام الذكاء الاصطناعي"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        # راكد: لم يتحرك منذ 30 يوم
        threshold_date = today - timedelta(days=30)
        stagnant_items = InventoryItem.objects.filter(last_movement_date__lt=threshold_date)

        for item in stagnant_items:
            AIDecisionAlert.objects.create(
                section='inventory',
                alert_type='منتج راكد',
                message=f"الصنف '{item.name}' لم يتحرك منذ أكثر من 30 يومًا.",
                level='warning'
            )

        # على وشك النفاد: الكمية أقل من الحد الأدنى
        critical_items = InventoryItem.objects.filter(quantity__lt=10)  # الحد يمكن تعديله من الإعدادات لاحقًا

        for item in critical_items:
            AIDecisionAlert.objects.create(
                section='inventory',
                alert_type='مخزون منخفض',
                message=f"الصنف '{item.name}' على وشك النفاد (الكمية = {item.quantity}).",
                level='danger'
            )

        self.stdout.write(self.style.SUCCESS("✅ تم تحليل المخزون وتنبيه الأصناف الحرجة والراكدة."))

