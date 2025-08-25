# ERP_CORE/departments/forms.py
from django import forms
from .models import Department
from core.templatetags.smart_hints import smart_hint  # ✅ إضافة التلميحات الذكية
from django.utils.safestring import mark_safe

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        labels = {
            'name': 'اسم القسم',
            'description': 'الوصف',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم القسم',
                'dir': 'rtl'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'وصف اختياري للقسم',
                'rows': 3,
                'dir': 'rtl'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ دمج التلميحات الذكية كـ help_text ديناميكي
        for field in self.fields:
            self.fields[field].help_text = mark_safe(smart_hint(field, 'departments'))
