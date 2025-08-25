# ERP_CORE/sales/management/commands/ai_recommender_task.py

from django.core.management.base import BaseCommand
from apps.sales.models import Sale, ProductProfitAnalysis
from apps.ai_decision.models import AIDecisionAlert
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Analyze sales data and recommend AI-based decisions.'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        stale_days = 30

        # ✅ 1. موديلات راكدة (لم تُباع منذ فترة)
        stale_models = ProductProfitAnalysis.objects.filter(
            last_sold_date__lt=today - timedelta(days=stale_days)
        )

        for model in stale_models:
            AIDecisionAlert.objects.get_or_create(
                section='sales',
                alert_type='موديل راكد',
                message=f"الموديل {model.product.name} لم يتم بيعه منذ أكثر من {stale_days} يومًا.",
                level='warning'
            )

        # ✅ 2. موديلات عالية الربحية → اقتراح بالترويج
        profitable_models = ProductProfitAnalysis.objects.filter(profit_margin__gte=0.4)

        for model in profitable_models:
            AIDecisionAlert.objects.get_or_create(
                section='sales',
                alert_type='اقتراح ترويج',
                message=f"الموديل {model.product.name} لديه هامش ربح {model.profit_margin * 100:.1f}%. يُفضل الترويج له.",
                level='info'
            )

        self.stdout.write(self.style.SUCCESS("✅ تم تنفيذ تحليل AI للمبيعات وإرسال التنبيهات الذكية."))