# ERP_CORE/ai_decision/ai_recommender.py

from apps.sales.models import Sale, SaleItem
from apps.products.models import Product
from django.utils import timezone
from apps.ai_decision.models import AIDecisionAlert
from collections import defaultdict
from datetime import timedelta

def analyze_sales_profitability():
    today = timezone.now().date()
    recent_sales = Sale.objects.filter(date__gte=today - timedelta(days=30))

    product_stats = defaultdict(lambda: {'total_qty': 0, 'total_profit': 0})

    for sale in recent_sales:
        for item in sale.items.all():
            cost = item.product.production_cost
            profit = (item.unit_price - cost) * item.quantity
            product_stats[item.product.id]['total_qty'] += item.quantity
            product_stats[item.product.id]['total_profit'] += profit

    low_demand_threshold = 3
    low_profit_threshold = 100  # Customize based on business needs

    for product_id, stats in product_stats.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        qty = stats['total_qty']
        profit = stats['total_profit']

        if qty <= low_demand_threshold:
            AIDecisionAlert.objects.create(
                section="sales",
                alert_type="منتج راكد",
                message=f"المنتج '{product.name}' يعتبر راكد (الكمية المباعة = {qty})",
                level="warning"
            )
        if profit < low_profit_threshold:
            AIDecisionAlert.objects.create(
                section="sales",
                alert_type="ربح منخفض",
                message=f"المنتج '{product.name}' حقق ربحًا منخفضًا ({profit:.2f})",
                level="info"
            )
        if qty > 10 and profit > 1000:
            AIDecisionAlert.objects.create(
                section="sales",
                alert_type="منتج عالي الأداء",
                message=f"المنتج '{product.name}' عالي الربحية ({profit:.2f}) ومطلوب بشدة (الكمية = {qty})",
                level="success"
            )
