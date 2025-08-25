from django import forms
from .models import Advance, Salary
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date

class AdvanceForm(forms.ModelForm):
    class Meta:
        model = Advance
        fields = ['employee', 'type', 'amount', 'date', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("يجب أن تكون قيمة السلفة أكبر من 0")
        return amount


class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ['employee', 'month', 'year', 'base_salary', 'production_bonus', 'deductions', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')

        # منع التكرار لنفس الشهر
        if employee and month and year:
            exists = Salary.objects.filter(employee=employee, month=month, year=year).exists()
            if exists and not self.instance.pk:
                raise ValidationError(_("تم تسجيل مرتب لهذا الموظف في هذا الشهر مسبقًا."))

        base_salary = cleaned_data.get('base_salary') or 0
        bonus = cleaned_data.get('production_bonus') or 0
        deductions = cleaned_data.get('deductions') or 0

        # حساب صافي المرتب تلقائي
        cleaned_data['final_salary'] = base_salary + bonus - deductions

        if cleaned_data['final_salary'] < 0:
            raise ValidationError(_("صافي المرتب لا يمكن أن يكون أقل من صفر."))

        return cleaned_data


# ✅ نموذج إدارة لائحة الخصومات والمكافآت
from django.forms import modelformset_factory
from .models import PolicySetting

PolicySettingFormSet = modelformset_factory(
    PolicySetting,
    fields=('key', 'value', 'description'),
    extra=0,
    widgets={
        'key': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        'value': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        'description': forms.TextInput(attrs={'class': 'form-control'}),
    }
)
