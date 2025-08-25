from django import forms
from .models import Evaluation

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
