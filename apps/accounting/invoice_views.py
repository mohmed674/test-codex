# ERP_CORE/accounting/invoice_views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.template.loader import get_template
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from weasyprint import HTML

from .models import (
    SalesInvoice, PurchaseInvoice, InvoiceItem
)
from .forms import SalesInvoiceForm, PurchaseInvoiceForm, InvoiceItemForm
from core.utils import export_to_excel


# ===================== helpers =====================

def _generate_invoice_number(model_cls, prefix: str) -> str:
    """
    يولّد رقم فاتورة تلقائيًا بالشكل:
    SI-YYYYMM-0001  أو  PI-YYYYMM-0001
    """
    today = timezone.now().date()
    yyyymm = today.strftime("%Y%m")
    base = f"{prefix}-{yyyymm}-"
    # نجيب آخر رقم لنفس الشهر
    last = (
        model_cls.objects
        .filter(number__startswith=base)
        .aggregate(mx=Max("number"))
        .get("mx")
    )
    if not last:
        seq = 1
    else:
        # آخر 4 أرقام
        try:
            seq = int(last.split("-")[-1]) + 1
        except Exception:
            seq = 1
    return f"{base}{seq:04d}"


# ============== فواتير المبيعات ==============

@login_required
def create_sales_invoice(request):
    """
    إنشاء فاتورة مبيعات + عناصرها باستخدام inline formset مربوط بـ sales_invoice.
    """
    ItemFormSet = inlineformset_factory(
        SalesInvoice, InvoiceItem,
        form=InvoiceItemForm,
        fk_name='sales_invoice',
        extra=1, can_delete=True
    )

    if request.method == 'POST':
        form = SalesInvoiceForm(request.POST)
        formset = ItemFormSet(request.POST, prefix='items')

        if form.is_valid() and formset.is_valid():
            invoice: SalesInvoice = form.save(commit=False)

            # ترقيم تلقائي لو الرقم غير مُدخل
            if not invoice.number:
                invoice.number = _generate_invoice_number(SalesInvoice, "SI")

            invoice.created_by = getattr(request.user, 'employee', None)
            if not invoice.date_issued:
                invoice.date_issued = timezone.now().date()
            invoice.save()

            formset.instance = invoice

            total = 0
            for f in formset.forms:
                if not getattr(f, "cleaned_data", None) or f.cleaned_data.get('DELETE'):
                    continue
                item = f.save(commit=False)
                item.sales_invoice = invoice
                item.purchase_invoice = None  # تأكيد
                item.save()
                total += (item.quantity or 0) * (item.unit_price or 0)

            # حذف العناصر المؤشرة للحذف
            for obj in formset.deleted_objects:
                obj.delete()

            invoice.total_amount = total
            invoice.save()

            messages.success(request, "✅ تم حفظ فاتورة المبيعات بنجاح.")
            return redirect('accounting:sales_invoice_detail', invoice.id)
        else:
            messages.error(request, "⚠️ تأكد من تعبئة الحقول بشكل صحيح.")
    else:
        form = SalesInvoiceForm()
        formset = ItemFormSet(prefix='items')

    return render(
        request,
        'accounting/invoices/sales_invoice_form.html',
        {'form': form, 'formset': formset}
    )


@login_required
def sales_invoice_detail(request, pk):
    invoice = get_object_or_404(SalesInvoice, pk=pk)
    items = InvoiceItem.objects.filter(sales_invoice=invoice).order_by('id')
    return render(
        request,
        'accounting/invoices/sales_invoice_detail.html',
        {'invoice': invoice, 'items': items}
    )


# ============== فواتير المشتريات ==============

@login_required
def create_purchase_invoice(request):
    """
    إنشاء فاتورة مشتريات + عناصرها باستخدام inline formset مربوط بـ purchase_invoice.
    """
    ItemFormSet = inlineformset_factory(
        PurchaseInvoice, InvoiceItem,
        form=InvoiceItemForm,
        fk_name='purchase_invoice',
        extra=1, can_delete=True
    )

    if request.method == 'POST':
        form = PurchaseInvoiceForm(request.POST)
        formset = ItemFormSet(request.POST, prefix='items')

        if form.is_valid() and formset.is_valid():
            invoice: PurchaseInvoice = form.save(commit=False)

            # ترقيم تلقائي لو الرقم غير مُدخل
            if not invoice.number:
                invoice.number = _generate_invoice_number(PurchaseInvoice, "PI")

            invoice.created_by = getattr(request.user, 'employee', None)
            if not invoice.date_issued:
                invoice.date_issued = timezone.now().date()
            invoice.save()

            formset.instance = invoice

            total = 0
            for f in formset.forms:
                if not getattr(f, "cleaned_data", None) or f.cleaned_data.get('DELETE'):
                    continue
                item = f.save(commit=False)
                item.purchase_invoice = invoice
                item.sales_invoice = None  # تأكيد
                item.save()
                total += (item.quantity or 0) * (item.unit_price or 0)

            for obj in formset.deleted_objects:
                obj.delete()

            invoice.total_amount = total
            invoice.save()

            messages.success(request, "✅ تم حفظ فاتورة المشتريات بنجاح.")
            return redirect('accounting:purchase_invoice_detail', invoice.id)
        else:
            messages.error(request, "⚠️ تأكد من تعبئة الحقول بشكل صحيح.")
    else:
        form = PurchaseInvoiceForm()
        formset = ItemFormSet(prefix='items')

    return render(
        request,
        'accounting/invoices/purchase_invoice_form.html',
        {'form': form, 'formset': formset}
    )


@login_required
def purchase_invoice_detail(request, pk):
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    items = InvoiceItem.objects.filter(purchase_invoice=invoice).order_by('id')
    return render(
        request,
        'accounting/invoices/purchase_invoice_detail.html',
        {'invoice': invoice, 'items': items}
    )


# ============== طباعة PDF ==============

@login_required
def print_invoice_pdf(request, invoice_type, pk):
    """
    طباعة PDF لفاتورة (مبيعات أو مشتريات) عبر WeasyPrint.
    """
    if invoice_type == "sales":
        invoice = get_object_or_404(SalesInvoice, pk=pk)
        template_name = 'accounting/invoices/sales_invoice_pdf.html'
        items = InvoiceItem.objects.filter(sales_invoice=invoice).order_by('id')
    else:
        invoice = get_object_or_404(PurchaseInvoice, pk=pk)
        template_name = 'accounting/invoices/purchase_invoice_pdf.html'
        items = InvoiceItem.objects.filter(purchase_invoice=invoice).order_by('id')

    html = get_template(template_name).render({'invoice': invoice, 'items': items})
    pdf_file = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{invoice_type}_invoice_{pk}.pdf"'
    return response


# ============== Dashboard + تصدير ==============

@login_required
def sales_invoice_dashboard(request):
    invoices = SalesInvoice.objects.select_related('customer').all()

    customer = request.GET.get('customer')
    status = request.GET.get('status')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if customer:
        invoices = invoices.filter(customer__name__icontains=customer)
    if status:
        invoices = invoices.filter(status=status)
    if date_from and date_to:
        invoices = invoices.filter(date_issued__range=[date_from, date_to])

    invoices = invoices.order_by('-date_issued')

    context = {
        'invoices': invoices,
        'filters': {
            'customer': customer or '',
            'status': status or '',
            'from': date_from or '',
            'to': date_to or '',
        }
    }
    return render(request, 'accounting/invoices/sales_invoice_dashboard.html', context)


@login_required
def sales_invoice_excel(request):
    invoices = SalesInvoice.objects.select_related('customer').all().order_by('-date_issued')

    data = []
    for inv in invoices:
        data.append({
            "رقم الفاتورة": inv.number,
            "العميل": inv.customer.name if inv.customer else '',
            "تاريخ الإصدار": inv.date_issued.strftime('%Y-%m-%d') if inv.date_issued else '',
            "الاستحقاق": inv.due_date.strftime('%Y-%m-%d') if inv.due_date else '',
            "الحالة": inv.get_status_display(),
            "المبلغ": float(inv.total_amount or 0),
        })

    return export_to_excel(data, filename="sales_invoices.xlsx")
