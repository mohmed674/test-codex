from django import forms
from .models import WorkflowRule

class WorkflowRuleForm(forms.ModelForm):
    class Meta:
        model = WorkflowRule
        fields = '__all__'
