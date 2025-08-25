from django import forms
from .models import DisciplineRecord

class DisciplineRecordForm(forms.ModelForm):
    class Meta:
        model = DisciplineRecord
        fields = ['employee', 'type', 'value', 'reason', 'created_by']
        labels = {
            'employee': 'الموظف',
            'type': 'نوع الإجراء',
            'value': 'القيمة (إن وجدت)',
            'reason': 'السبب',
            'created_by': 'تم بواسطة',
        }
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-control',
            }),
            'type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: خصم - مكافأة - إنذار',
                'dir': 'rtl'
            }),
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'القيمة إن وجدت'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'سبب الإجراء',
                'dir': 'rtl'
            }),
            'created_by': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المسؤول',
                'dir': 'rtl'
            }),
        }

    def clean_value(self):
        value = self.cleaned_data.get('value')
        if value is not None and value < 0:
            raise forms.ValidationError("❌ لا يمكن أن تكون القيمة سالبة.")
        return value
