from django import forms
from .models import LegalCase

class LegalCaseForm(forms.ModelForm):
    class Meta:
        model = LegalCase
        fields = '__all__'
