from django import forms
from .models import MaterialPlanning

class MaterialPlanningForm(forms.ModelForm):
    class Meta:
        model = MaterialPlanning
        fields = ['product', 'planned_quantity', 'required_date']
