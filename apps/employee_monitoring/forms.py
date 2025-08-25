from django import forms
from .models import MonitoringRecord, Evaluation

class MonitoringForm(forms.ModelForm):
    class Meta:
        model = MonitoringRecord
        fields = ['employee', 'status', 'notes']

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['employee', 'score', 'date']
