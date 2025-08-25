# ERP_CORE/monitoring/forms.py

from django import forms
from .models import DistributionOrder, Shipment

class DistributionOrderForm(forms.ModelForm):
    class Meta:
        model = DistributionOrder
        fields = ['client', 'product_name', 'quantity', 'status']
        widgets = {
            'status': forms.Select(choices=[('Pending', 'قيد الانتظار'), ('Confirmed', 'تم التأكيد'), ('Delivered', 'تم التسليم')]),
        }

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['tracking_number', 'order', 'status']
        widgets = {
            'status': forms.Select(choices=[('In Transit', 'في الطريق'), ('Delivered', 'تم التسليم'), ('Delayed', 'تأخر')]),
        }
