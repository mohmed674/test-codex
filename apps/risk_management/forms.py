from django import forms
from .models import Risk

class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = '__all__'
