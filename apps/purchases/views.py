# ERP_CORE/purchases/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import PurchaseRequest, PurchaseOrder, PurchaseInvoice
from .forms import PurchaseRequestForm, PurchaseItemFormSet, PurchaseOrderForm, PurchaseInvoiceForm
from django.contrib import messages
from django.forms import modelform_factory


def purchase_request_create(request):
    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST)
        formset = PurchaseItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            purchase_request = form.save(commit=False)
            purchase_request.requested_by = request.user.employee
            purchase_request.save()
            formset.instance = purchase_request
            formset.save()
            messages.success(request, "تم إرسال طلب الشراء بنجاح.")
            return redirect('purchases:purchase_list')
    else:
        form = PurchaseRequestForm()
        formset = PurchaseItemFormSet()
    return render(request, 'purchases/purchase_request_form.html', {
        'form': form,
        'formset': formset
    })


def purchase_list(request):
    requests = PurchaseRequest.objects.all().order_by('-created_at')
    return render(request, 'purchases/purchase_list.html', {'requests': requests})


def purchase_order_create(request, request_id):
    purchase_request = get_object_or_404(PurchaseRequest, id=request_id)
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.purchase_request = purchase_request
            order.save()
            messages.success(request, "تم إنشاء أمر الشراء.")
            return redirect('purchases:purchase_list')
    else:
        form = PurchaseOrderForm()
    return render(request, 'purchases/purchase_order_form.html', {
        'form': form,
        'purchase_request': purchase_request
    })


def purchase_invoice_create(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    if request.method == 'POST':
        form = PurchaseInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.order = order
            invoice.save()
            messages.success(request, "تم تسجيل الفاتورة.")
            return redirect('purchases:purchase_list')
    else:
        form = PurchaseInvoiceForm()
    return render(request, 'purchases/purchase_invoice_form.html', {
        'form': form,
        'order': order
    })


from django.shortcuts import render

def index(request):
    return render(request, 'purchases/index.html')


def app_home(request):
    return render(request, 'apps/purchases/home.html', {'app': 'purchases'})
