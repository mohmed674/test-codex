# ERP_CORE/sales/ai_recommender.py

from django.utils import timezone
from apps.sales.models import Sale, Product
from apps.ai_decision.models import AIDecisionAlert
from django.db.models import Sum, Count, F, Max
import datetime


def detect_stagnant_products(threshold_days=30, min_sales=2):
    today = timezone.now().date()
    stagnant_products = Product.objects.annotate(
        total_sales=Sum('sale__quantity'),
        last_sale_date=Max('sale__sale_date')
    ).filter(
        last_sale_date__lt=today - datetime.timedelta(days=threshold_days),
        total_sales__lt=min_sales
    )

    for product in stagnant_products:
        AIDecisionAlert.objects.create(
            section='sales',
            alert_type='موديل راكد',
            message=f"الموديل '{product.name}' راكد: مبيعات منخفضة منذ أكثر من {threshold_days} يومًا.",
            level='warning'
        )

        # (اختياري) وضع علامة على المنتج في قاعدة البيانات
        product.is_stagnant = True
        product.save()


def suggest_focus_on_profitable_models(min_profit_margin=50):
    profitable_products = Product.objects.annotate(
        total_sales=Sum(F('sale__quantity') * F('sale__price')),
        total_cost=F('cost_price') * Sum('sale__quantity')
    ).filter(
        total_sales__isnull=False,
        total_cost__isnull=False
    )

    for product in profitable_products:
        if product.total_cost == 0:
            continue
        margin = ((product.total_sales - product.total_cost) / product.total_cost) * 100
        if margin >= min_profit_margin:
            AIDecisionAlert.objects.create(
                section='sales',
                alert_type='موديل عالي الربحية',
                message=f"الموديل '{product.name}' يحقق ربحية عالية بنسبة {round(margin, 2)}٪. ينصح بالتركيز عليه.",
                level='info'
            )