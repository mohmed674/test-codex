# ERP_CORE/products/ai.py
from apps.ai_decision.models import AIDecisionAlert
from .models import Product

def detect_unsold_products():
    for product in Product.objects.all():
        if product.total_sales == 0:
            AIDecisionAlert.objects.create(
                section='products',
                alert_type='منتج راكد',
                level='info',
                message=f"المنتج {product.name} لم يتم بيعه حتى الآن."
            )