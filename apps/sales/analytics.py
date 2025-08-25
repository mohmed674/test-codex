# ERP_CORE/sales/analytics.py

from .models import Sale
from django.db.models import Sum, F, FloatField, ExpressionWrapper

def profitability_by_model():
    sales = Sale.objects.values('product__model_name').annotate(
        total_sales=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=FloatField())),
        total_cost=Sum('product__cost_price'),
    )

    for s in sales:
        s['profit'] = round(s['total_sales'] - s.get('total_cost', 0), 2)
        s['profit_margin'] = round((s['profit'] / s['total_sales']) * 100, 2) if s['total_sales'] > 0 else 0
    return sales

def profitability_by_customer():
    sales = Sale.objects.values('customer__name').annotate(
        total_sales=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=FloatField())),
        total_cost=Sum('product__cost_price'),
    )

    for s in sales:
        s['profit'] = round(s['total_sales'] - s.get('total_cost', 0), 2)
        s['profit_margin'] = round((s['profit'] / s['total_sales']) * 100, 2) if s['total_sales'] > 0 else 0
    return sales
