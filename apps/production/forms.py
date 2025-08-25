from django import forms
from .models import (
    ProductionOrder,
    ProductionStage,
    MaterialConsumption,
    QualityCheck,
    ProductVersion
)

class ProductionOrderForm(forms.ModelForm):
    class Meta:
        model = ProductionOrder
        fields = ['order_number', 'product', 'start_date', 'end_date', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ProductionStageForm(forms.ModelForm):
    class Meta:
        model = ProductionStage
        fields = ['order', 'stage_name', 'start_time', 'end_time', 'completed']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class MaterialConsumptionForm(forms.ModelForm):
    class Meta:
        model = MaterialConsumption
        fields = ['order', 'material', 'quantity_used', 'unit', 'wastage']

class QualityCheckForm(forms.ModelForm):
    class Meta:
        model = QualityCheck
        fields = ['product', 'order', 'stage', 'inspector', 'status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class ProductVersionForm(forms.ModelForm):
    class Meta:
        model = ProductVersion
        # احذف description نهائياً من الحقول والودجت
        fields = ['product', 'version_code', 'season', 'created_by', 'change_notes', 'is_active']
        widgets = {
            'change_notes': forms.Textarea(attrs={'rows': 2}),
        }
