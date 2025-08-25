from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

from .models import SaleInvoice, SaleItem, SalesPerformance, SmartSalesSuggestion
from .forms import SaleInvoiceForm, SaleItemForm
from core.utils import render_to_pdf, export_to_excel
from .voice_alerts import check_sales_anomalies


# ✅ إنشاء عملية بيع مع تنبيه صوتي
@login_required
def create_sale(request):
    if request.method == 'POST':
        form = SaleInvoiceForm(request.POST)
        if form.is_valid():
            sale = form.save()
            check_sales_anomalies(sale)  # ✅ تنبيه صوتي تلقائي
            return redirect('sales:sale_list')
    else:
        form = SaleInvoiceForm()
    return render(request, 'sales/sale_form.html', {'form': form})


# ✅ لوحة مبيعات ذكية
@login_required
def sales_dashboard_view(request):
    # اجلب الفواتير مع العميل والشريك لتقليل الاستعلامات
    invoices_qs = (
        SaleInvoice.objects
        .select_related('client', 'client__partner')
        .all()
    )

    # إجمالي المبيعات (أكثر كفاءة من sum في بايثون)
    total_sales = invoices_qs.aggregate(total=Sum('total_amount'))['total'] or 0

    # أفضل العملاء حسب إجمالي الفواتير
    # ملاحظة: Client مفيهوش name، الاسم في Partner المرتبط
    top_clients = (
        SaleInvoice.objects
        .values('client__partner__name')                     # ← الاسم الصحيح
        .annotate(total=Sum('total_amount'))
        .order_by('-total')[:5]
    )

    suggestions = SmartSalesSuggestion.objects.all()

    # لو محتاج تعرض كل الفواتير في الجدول
    invoices = invoices_qs

    return render(request, 'sales/dashboard.html', {
        'invoices': invoices,
        'total_sales': total_sales,
        'top_clients': top_clients,
        'suggestions': suggestions,
    })


# ✅ عرض فواتير البيع + PDF/Excel
@login_required
def invoice_list_view(request):
    invoices = (
        SaleInvoice.objects
        .select_related('client', 'client__partner')
        .all()
    )

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf("sales/invoice_pdf.html", {"invoices": invoices, "request": request})

    if request.GET.get("export") == "1":
        data = []
        for i in invoices:
            partner = getattr(getattr(i, 'client', None), 'partner', None)
            client_name = getattr(partner, 'name', '')  # يتفادى AttributeError
            data.append({
                "رقم الفاتورة": i.invoice_number,
                "العميل": client_name,                  # ← بدل i.client.name
                "الإجمالي": i.total_amount,
                "التاريخ": i.date.strftime("%Y-%m-%d"),
            })
        return export_to_excel(data, filename="sales_invoices.xlsx")

    return render(request, 'sales/invoice_list.html', {'invoices': invoices})


# ✅ إنشاء فاتورة جديدة
@login_required
def invoice_create_view(request):
    if request.method == 'POST':
        form = SaleInvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sales:invoice_list')
    else:
        form = SaleInvoiceForm()
    return render(request, 'sales/invoice_form.html', {'form': form})


# ✅ عرض أداء المبيعات
@login_required
def performance_view(request):
    performances = SalesPerformance.objects.select_related('employee').all()
    return render(request, 'sales/performance.html', {'performances': performances})


# ✅ توصيات AI الذكية لتحسين المبيعات
@login_required
def smart_suggestions_view(request):
    suggestions = SmartSalesSuggestion.objects.all()
    return render(request, 'sales/suggestions.html', {'suggestions': suggestions})


# ✅ طباعة الفاتورة - نسخة HTML للطباعة العادية
@login_required
def print_invoice(request, invoice_id):
    invoice = get_object_or_404(SaleInvoice, pk=invoice_id)
    return render(request, 'sales/sale_invoice_print.html', {'invoice': invoice})


# ✅ طباعة الفاتورة - نسخة PDF قابلة للتحميل
@login_required
def invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(SaleInvoice, pk=invoice_id)
    return render_to_pdf('sales/sale_invoice_print.html', {'invoice': invoice})


from django.shortcuts import render

def index(request):
    return render(request, 'sales/index.html')


def app_home(request):
    return render(request, 'apps/sales/home.html', {'app': 'sales'})
