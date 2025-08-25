# D:\ERP_CORE\accounting\views.py
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import csv

from weasyprint import HTML
from core.utils import export_to_excel

from .models import (
    JournalEntry, JournalItem,
    Supplier, Customer,
    AccountingSuggestionLog, SupplierInvoice,
    CashTransaction
)
from apps.products.models import Product

from .forms import (
    JournalEntryForm, JournalItemForm,
    JournalItemFormSet
)
from .ai_accounting_assistant import AIAccountingAssistant

from rest_framework import viewsets
from .serializers import SupplierInvoiceSerializer


@login_required
def home(request):
    return render(request, 'accounting/index.html')


@login_required
def financial_analysis_view(request):
    monthly_data = (
        JournalEntry.objects
        .annotate(month=TruncMonth('date'))
        .values('month', 'entry_type')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    income_data, expense_data = {}, {}
    for record in monthly_data:
        month = record['month'].strftime('%Y-%m')
        if record['entry_type'] == 'credit':
            income_data[month] = record['total']
        else:
            expense_data[month] = record['total']

    analysis = []
    months = sorted(set(income_data) | set(expense_data))
    for month in months:
        income = income_data.get(month, 0) or 0
        expense = expense_data.get(month, 0) or 0
        profit = income - expense
        analysis.append({
            'month': month,
            'income': float(income),
            'expense': float(expense),
            'profit': float(profit)
        })

    return render(request, 'accounting/financial_analysis.html', {
        'analysis': analysis
    })


@login_required
def journal_dashboard(request):
    entries = JournalEntry.objects.all().order_by('-date')
    return render(request, 'accounting/journal/journal_dashboard.html', {
        'entries': entries
    })


@login_required
def journal_create(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = getattr(request.user, 'employee', None)
            entry.save()
            messages.success(request, "✅ تم إنشاء القيد بنجاح.")
            return redirect('accounting:journal_detail', entry.pk)
        else:
            messages.error(request, "⚠️ تأكد من تعبئة الحقول المطلوبة.")
    else:
        form = JournalEntryForm()
    return render(request, 'accounting/journal/journal_form.html', {'form': form})


@login_required
def journal_detail(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk)
    items = JournalItem.objects.filter(entry=entry)
    return render(request, 'accounting/journal/journal_detail.html', {
        'entry': entry,
        'items': items
    })


@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'accounting/partners/supplier_list.html', {
        'suppliers': suppliers
    })


@login_required
def supplier_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Supplier.objects.create(name=name)
            messages.success(request, "✅ تم إضافة المورد بنجاح.")
            return redirect('accounting:supplier_list')
        else:
            messages.error(request, "⚠️ يرجى إدخال اسم المورد.")
    return render(request, 'accounting/partners/supplier_form.html')


@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('name')
    return render(request, 'accounting/partners/customer_list.html', {
        'customers': customers
    })


@login_required
def customer_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Customer.objects.create(name=name)
            messages.success(request, "✅ تم إضافة العميل بنجاح.")
            return redirect('accounting:customer_list')
        else:
            messages.error(request, "⚠️ يرجى إدخال اسم العميل.")
    return render(request, 'accounting/partners/customer_form.html')


@login_required
def product_list(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'accounting/products/product_list.html', {
        'products': products
    })


@login_required
def product_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        if name and price:
            try:
                price = float(price)
                Product.objects.create(name=name, price=price)
                messages.success(request, "✅ تم إضافة المنتج بنجاح.")
                return redirect('accounting:product_list')
            except ValueError:
                messages.error(request, "⚠️ يرجى إدخال سعر صالح.")
        else:
            messages.error(request, "⚠️ يرجى إدخال جميع البيانات المطلوبة.")
    return render(request, 'accounting/products/product_form.html')


@login_required
def export_accounting_excel(request):
    data = []
    entries = JournalEntry.objects.all().order_by('-date')
    for entry in entries:
        data.append({
            'التاريخ': entry.date.strftime('%Y-%m-%d'),
            'الوصف': entry.description,
            'المبلغ': entry.debit or entry.credit
        })
    return export_to_excel(data, filename='accounting_journal.xlsx')


@login_required
def export_accounting_pdf(request):
    entries = JournalEntry.objects.all().order_by('-date')
    html = get_template('accounting/journal/journal_pdf.html').render({
        'entries': entries
    })
    pdf_file = HTML(string=html).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="accounting_journal.pdf"'
    return response


@login_required
def export_accounting_csv(request):
    entries = JournalEntry.objects.all().order_by('-date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="accounting_journal.csv"'
    writer = csv.writer(response)
    writer.writerow(['التاريخ', 'الوصف', 'المبلغ'])
    for entry in entries:
        writer.writerow([
            entry.date.strftime('%Y-%m-%d'),
            entry.description,
            entry.debit or entry.credit
        ])
    return response


@login_required
def reports_overview_view(request):
    return render(request, 'accounting/reports/reports_overview.html')


@login_required
def guided_journal_entry_view(request):
    assistant = AIAccountingAssistant(user=request.user)

    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            desc = form.cleaned_data['description']
            amt = form.cleaned_data['amount']
            trx_type = request.POST.get('transaction_type', '')

            entry = assistant.generate_entry(desc, amt, trx_type)
            if entry:
                messages.success(request, '✅ تم تسجيل القيد تلقائيًا باستخدام الذكاء الاصطناعي.')
                return redirect('accounting:journal_dashboard')
            else:
                for _, msg in assistant.get_alerts():
                    messages.error(request, f"⚠️ {msg}")
    else:
        form = JournalEntryForm()

    return render(request, 'accounting/guided_entry.html', {'form': form})


@login_required
def journal_entry_create_view(request):
    form = JournalEntryForm(request.POST or None)
    formset = JournalItemFormSet(request.POST or None)
    assistant = AIAccountingAssistant(user=request.user)
    suggestion = None

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            entry = form.save(commit=False)
            entry.created_by = getattr(request.user, 'employee', None)
            entry.save()
            formset.instance = entry
            formset.save()
            messages.success(request, "✅ تم إنشاء القيد بنجاح.")
            return redirect('accounting:journal_dashboard')
        else:
            desc = request.POST.get('description')
            amt = request.POST.get('amount')
            trx_type = request.POST.get('transaction_type', '')
            suggestion = assistant.generate_entry(desc, amt, trx_type)

            if suggestion:
                messages.info(request, "💡 تم توليد اقتراح تلقائي للحسابات.")
            else:
                for _, msg in assistant.get_alerts():
                    messages.error(request, f"⚠️ {msg}")

    return render(request, 'accounting/journal_entry_form.html', {
        'form': form,
        'formset': formset,
        'suggestion': suggestion,
    })


@login_required
def suggestion_log_view(request):
    suggestions = AccountingSuggestionLog.objects.all().order_by('-timestamp')
    return render(request, 'accounting/suggestion_log.html', {
        'suggestions': suggestions
    })


class SupplierInvoiceViewSet(viewsets.ModelViewSet):
    queryset = SupplierInvoice.objects.all()
    serializer_class = SupplierInvoiceSerializer
    filterset_fields = ['supplier', 'status', 'payment_method', 'date_issued', 'due_date']


from django.shortcuts import render

def index(request):
    return render(request, 'accounting/index.html')


def app_home(request):
    return render(request, 'apps/accounting/home.html', {'app': 'accounting'})
