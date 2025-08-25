from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML
from core.utils import export_to_excel
from .models import (
    SalesInvoice, PurchaseInvoice, Expense, Asset,
    JournalEntry, PaymentOrder, CashTransaction, Invoice
)
from datetime import datetime
from django.db.models import Sum


# 📊 فواتير المبيعات
def sales_report(request):
    invoices = SalesInvoice.objects.select_related('customer')
    customer = request.GET.get('customer')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if customer:
        invoices = invoices.filter(customer_id=customer)
    if date_from and date_to:
        invoices = invoices.filter(date_issued__range=[date_from, date_to])

    context = {'invoices': invoices}
    return render(request, 'accounting/reports/sales_report.html', context)


# 🧾 فواتير المشتريات
def purchase_report(request):
    invoices = PurchaseInvoice.objects.select_related('supplier')
    supplier = request.GET.get('supplier')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if supplier:
        invoices = invoices.filter(supplier_id=supplier)
    if date_from and date_to:
        invoices = invoices.filter(date_issued__range=[date_from, date_to])

    context = {'invoices': invoices}
    return render(request, 'accounting/reports/purchase_report.html', context)


# 💸 المصروفات
def expense_report(request):
    expenses = Expense.objects.all()
    category = request.GET.get('category')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if category:
        expenses = expenses.filter(category=category)
    if date_from and date_to:
        expenses = expenses.filter(date__range=[date_from, date_to])

    context = {'expenses': expenses}
    return render(request, 'accounting/reports/expense_report.html', context)


# 🏢 الأصول الثابتة
def asset_report(request):
    assets = Asset.objects.all()
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if date_from and date_to:
        assets = assets.filter(purchase_date__range=[date_from, date_to])

    context = {'assets': assets}
    return render(request, 'accounting/reports/asset_report.html', context)


# 📘 القيود اليومية
def journal_report(request):
    entries = JournalEntry.objects.all()
    account = request.GET.get('account')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if account:
        entries = entries.filter(account__id=account)
    if date_from and date_to:
        entries = entries.filter(date__range=[date_from, date_to])

    context = {'entries': entries}
    return render(request, 'accounting/reports/journal_report.html', context)


# 💰 أوامر القبض والصرف
def cash_transactions_report(request):
    transactions = CashTransaction.objects.all()
    method = request.GET.get('method')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if method:
        transactions = transactions.filter(method=method)
    if date_from and date_to:
        transactions = transactions.filter(date__range=[date_from, date_to])

    context = {'transactions': transactions}
    return render(request, 'accounting/reports/cash_transactions_report.html', context)


# 📋 تقرير المدفوعات حسب وسيلة الدفع (المحافظ الإلكترونية أو غيرها)
def payments_by_method_report(request):
    method = request.GET.get('method')   # مثل: vodafone / bank / instapay...
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    invoices = Invoice.objects.select_related('customer').all()

    if method:
        invoices = invoices.filter(payment_method=method)
    if date_from and date_to:
        invoices = invoices.filter(date_issued__range=[date_from, date_to])

    report_data = (
        invoices.values('customer__name')
        .annotate(total_paid=Sum('total_amount'))
        .order_by('-total_paid')
    )

    return render(request, 'accounting/reports/payments_by_method_report.html', {
        'data': report_data,
        'method': method,
        'date_from': date_from,
        'date_to': date_to,
    })


# 🧾 تصدير PDF لأي تقرير
def render_report_pdf(request, template_name, context_data, filename="report.pdf"):
    html = get_template(template_name).render(context_data)
    pdf = HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response['Content-Disposition'] = f'filename="{filename}"'
    return response


# 📊 تصدير Excel لأي تقرير
def render_report_excel(data_list, filename="report.xlsx"):
    return export_to_excel(data_list, filename=filename)
