from django import forms
from .models import MaintenanceLog, MaintenanceRequest

class MaintenanceLogForm(forms.ModelForm):
    class Meta:
        model = MaintenanceLog
        fields = [
            'machine',
            'issue',
            'action_taken',
            'technician',
            'maintenance_date',
            'next_maintenance',
        ]
        widgets = {
            'maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'next_maintenance': forms.DateInput(attrs={'type': 'date'}),
        }


class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = [
            'machine',
            'reported_by',
            'issue_description',
            'status',
            'resolution_notes',
        ]
        widgets = {
            'issue_description': forms.Textarea(attrs={'rows': 3}),
            'resolution_notes': forms.Textarea(attrs={'rows': 2}),
        }
