# ai_decision/tasks.py

from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, F

from apps.sales.models import SaleItem
from apps.products.models import FinishedProduct
from apps.ai_decision.models import AIDecisionAlert

@shared_task
def analyze_product_sales(mode='daily'):
    now = timezone.now()

    if mode == 'daily':
        since = now - timedelta(days=1)
    elif mode == 'weekly':
        since = now - timedelta(days=7)
    elif mode == 'monthly':
        since = now - timedelta(days=30)
    else:
        since = now - timedelta(days=1)  # fallback

    # ✅ احصل على كل البنود المرتبطة بتاريخ حديث حسب الفاتورة
    sales = SaleItem.objects.filter(invoice__date__gte=since)

    # ✅ تجميع إجمالي الكمية والإيرادات حسب المنتج
    product_data = sales.values('product__id', 'product__name').annotate(
        total_sales=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('unit_price')),
    )

    for data in product_data:
        product_id = data['product__id']
        product_name = data['product__name']
        total_sales = data['total_sales']
        total_revenue = data['total_revenue']

        try:
            product = FinishedProduct.objects.get(id=product_id)
            production_cost = product.production_cost or 0
            profit = total_revenue - production_cost

            if total_sales < 3:
                AIDecisionAlert.objects.create(
                    section="sales",
                    alert_type="منتج راكد",
                    message=f"المنتج '{product_name}' لم يحقق مبيعات ({mode})",
                    level="warning"
                )

            if profit < 0:
                AIDecisionAlert.objects.create(
                    section="sales",
                    alert_type="خسارة في منتج",
                    message=f"المنتج '{product_name}' يحقق خسارة ({mode})",
                    level="danger"
                )

        except FinishedProduct.DoesNotExist:
            continue
