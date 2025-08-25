from django import forms
from .models import (
    JobTitle, Unit, EvaluationCriteria,
    ProductionStageType, RiskThreshold, DepartmentRole
)


class JobTitleForm(forms.ModelForm):
    class Meta:
        model = JobTitle
        fields = '__all__'
        widgets = {
            'salary_type': forms.Select(attrs={'class': 'form-select'}),
            'default_piece_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'default_daily_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'linked_to_production_stage': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'abbreviation': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_type': forms.Select(attrs={'class': 'form-select'}),
            'conversion_factor': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class EvaluationCriteriaForm(forms.ModelForm):
    class Meta:
        model = EvaluationCriteria
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'criteria_type': forms.Select(attrs={'class': 'form-select'}),
        }


class ProductionStageTypeForm(forms.ModelForm):
    class Meta:
        model = ProductionStageType
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'estimated_duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'requires_machine': forms.CheckboxInput(),
            'linked_job_titles': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }


class RiskThresholdForm(forms.ModelForm):
    class Meta:
        model = RiskThreshold
        fields = '__all__'
        widgets = {
            'risk_type': forms.TextInput(attrs={'class': 'form-control'}),
            'threshold_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'severity_level': forms.Select(attrs={'class': 'form-select'}),
            'action_required': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'trigger_auto_action': forms.CheckboxInput(),
        }


class DepartmentRoleForm(forms.ModelForm):
    class Meta:
        model = DepartmentRole
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
