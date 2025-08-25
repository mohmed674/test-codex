# ERP_CORE/purchases/forms.py

from django import forms
from .models import PurchaseRequest, PurchaseItem, PurchaseOrder, PurchaseInvoice
from django.forms import inlineformset_factory


class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ['department', 'purpose']


PurchaseItemFormSet = inlineformset_factory(
    PurchaseRequest, PurchaseItem,
    fields=('product', 'quantity', 'notes'),
    extra=1,
    can_delete=True
)


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier_name', 'total_amount', 'order_date', 'expected_delivery', 'is_delivered']


class PurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoice
        fields = ['invoice_number', 'invoice_date', 'amount', 'account']
