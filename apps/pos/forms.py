from django import forms
from .models import POSOrder, POSOrderItem

class POSOrderForm(forms.ModelForm):
    class Meta:
        model = POSOrder
        fields = ['client', 'payment_method', 'paid']

class POSOrderItemForm(forms.ModelForm):
    class Meta:
        model = POSOrderItem
        fields = ['product', 'quantity', 'unit_price']
