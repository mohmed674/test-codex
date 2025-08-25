# ERP_CORE/employees/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
import re

from apps.employees.models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'name', 'job_title', 'gender', 'department', 'national_id',
            'phone', 'hire_date', 'active',
            'total_rewards', 'total_deductions', 'total_warnings',
            'total_evaluations', 'evaluation_score', 'behavior_status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'name'}),
            'job_title': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '14', 'inputmode': 'numeric'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'tel'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'total_rewards': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'total_deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'total_warnings': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0'}),
            'total_evaluations': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0'}),
            'evaluation_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'behavior_status': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'الاسم',
            'job_title': 'المسمى الوظيفي',
            'gender': 'النوع',
            'department': 'القسم',
            'national_id': 'الرقم القومي',
            'phone': 'رقم الهاتف',
            'hire_date': 'تاريخ التعيين',
            'active': 'نشط؟',
            'total_rewards': 'إجمالي المكافآت',
            'total_deductions': 'إجمالي الخصومات',
            'total_warnings': 'عدد الإنذارات',
            'total_evaluations': 'عدد التقييمات',
            'evaluation_score': 'متوسط التقييم',
            'behavior_status': 'الحالة السلوكية',
        }
        help_texts = {
            'national_id': 'أدخل 14 رقمًا بدون مسافات.',
        }

    # ===== Field-level validations =====
    def clean_national_id(self):
        nid = (self.cleaned_data.get('national_id') or '').strip()
        if nid:
            if not re.fullmatch(r'\d{14}', nid):
                raise ValidationError('الرقم القومي يجب أن يكون 14 رقمًا.')
        return nid or None

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        if phone:
            # السماح بـ + وأرقام ومسافات وشرطات
            if not re.fullmatch(r'[+\d][\d\s\-]{6,20}', phone):
                raise ValidationError('رقم الهاتف غير صالح.')
            # تطبيع: إزالة مسافات إضافية
            phone = re.sub(r'\s+', ' ', phone)
        return phone or None

    def clean_hire_date(self):
        hire_date = self.cleaned_data.get('hire_date')
        if hire_date and hire_date > timezone.localdate():
            raise ValidationError('تاريخ التعيين لا يمكن أن يكون في المستقبل.')
        return hire_date

    def clean_evaluation_score(self):
        score = self.cleaned_data.get('evaluation_score')
        if score is not None:
            if score < 0 or score > 100:
                raise ValidationError('متوسط التقييم يجب أن يكون بين 0 و 100.')
        return score

    # ===== Form-level validations =====
    def clean(self):
        cleaned = super().clean()

        def _nonneg(name, label):
            val = cleaned.get(name)
            if val is not None and val < 0:
                self.add_error(name, f'{label} لا يمكن أن يكون سالبًا.')

        _nonneg('total_rewards', 'إجمالي المكافآت')
        _nonneg('total_deductions', 'إجمالي الخصومات')
        _nonneg('total_warnings', 'عدد الإنذارات')
        _nonneg('total_evaluations', 'عدد التقييمات')

        return cleaned

    # ===== Save normalization =====
    def save(self, commit=True):
        obj: Employee = super().save(commit=False)
        if obj.name:
            obj.name = obj.name.strip()
        if commit:
            obj.save()
            self.save_m2m()
        return obj
