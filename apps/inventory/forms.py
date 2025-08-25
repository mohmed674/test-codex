from django import forms
from .models import InventoryItem, InventoryMovement, Warehouse

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['product', 'warehouse', 'quantity', 'unit', 'min_threshold']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'min_threshold': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class InventoryTransactionForm(forms.ModelForm):
    class Meta:
        model = InventoryMovement
        fields = ['item', 'movement_type', 'quantity', 'note']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'movement_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class InventoryLocationForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'location', 'manager', 'note']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'manager': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
