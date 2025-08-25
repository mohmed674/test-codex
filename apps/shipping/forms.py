from django import forms
from .models import Shipment

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['invoice', 'client', 'company', 'tracking_number', 'status', 'cost', 'payment_method']
