from datetime import timedelta

from django.shortcuts import render
from django.db.models import Sum, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone

import json
from django.core.serializers.json import DjangoJSONEncoder

from apps.sales.models import SaleInvoice
from apps.accounting.models import CashTransaction
from apps.products.models import Product
from apps.clients.models import Client
from apps.employees.models import Employee


def main_dashboard(request):
    # إحصائيات عامة
    total_sales = SaleInvoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_transactions = CashTransaction.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_products = Product.objects.count()
    total_clients = Client.objects.count()
    total_employees = Employee.objects.count()

    # متوسط المبيعات الشهرية (باستخدام الحقل الصحيح: date)
    avg_monthly = (
        SaleInvoice.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(monthly_total=Sum('total_amount'))
        .aggregate(avg=Avg('monthly_total'))
    )['avg'] or 0

    # مبيعات الشهر الحالي (بتاريخ محلي)
    today = timezone.localdate()
    start_of_month = today.replace(day=1)
    current_month_sales = (
        SaleInvoice.objects.filter(date__gte=start_of_month)
        .aggregate(total=Sum('total_amount'))['total'] or 0
    )

    # حساب نسبة النمو الشهري
    last_month_end = start_of_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    last_month_sales = (
        SaleInvoice.objects.filter(date__range=[last_month_start, last_month_end])
        .aggregate(total=Sum('total_amount'))['total'] or 0
    )
    growth_rate = round(((current_month_sales - last_month_sales) / last_month_sales) * 100, 2) if last_month_sales > 0 else 0

    # مبيعات حسب الأشهر (للرسم البياني)
    sales_by_month = list(
        SaleInvoice.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    # JSON آمن للتمبليت
    sales_by_month_json = json.dumps(sales_by_month, cls=DjangoJSONEncoder)

    context = {
        'total_sales': total_sales,
        'total_transactions': total_transactions,
        'total_products': total_products,
        'total_clients': total_clients,
        'total_employees': total_employees,
        'average_monthly_sales': avg_monthly,
        'current_month_sales': current_month_sales,
        'last_month_sales': last_month_sales,
        'growth_rate': growth_rate,
        'sales_by_month_json': sales_by_month_json,
    }

    return render(request, 'dashboard_center/overview.html', context)


from django.shortcuts import render

def index(request):
    return render(request, 'dashboard_center/index.html')


def app_home(request):
    return render(request, 'apps/dashboard_center/home.html', {'app': 'dashboard_center'})
