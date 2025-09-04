# apps/payroll/forms.py

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Advance, PolicySetting, Salary


class AdvanceForm(forms.ModelForm):
    class Meta:
        model = Advance
        fields = ["employee", "type", "amount", "date", "note"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "note": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "amount": forms.NumberInput(
                attrs={"step": "0.01", "class": "form-control"}
            ),
        }

    def clean_amount(self) -> Decimal:
        amount = self.cleaned_data.get("amount")
        if amount is None or amount <= 0:  # handle None to satisfy type checkers
            raise forms.ValidationError(_("يجب أن تكون قيمة السلفة أكبر من 0"))
        return amount


class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = [
            "employee",
            "month",
            "year",
            "base_salary",
            "production_bonus",
            "deductions",
            "note",
        ]
        widgets = {
            "note": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "base_salary": forms.NumberInput(
                attrs={"step": "0.01", "class": "form-control"}
            ),
            "production_bonus": forms.NumberInput(
                attrs={"step": "0.01", "class": "form-control"}
            ),
            "deductions": forms.NumberInput(
                attrs={"step": "0.01", "class": "form-control"}
            ),
        }

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        employee = cleaned_data.get("employee")
        month = cleaned_data.get("month")
        year = cleaned_data.get("year")

        # منع التكرار لنفس الشهر
        if employee and month and year:
            exists = Salary.objects.filter(employee=employee, month=month, year=year)
            if self.instance.pk:
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                raise ValidationError(
                    _("تم تسجيل مرتب لهذا الموظف في هذا الشهر مسبقًا.")
                )

        base_salary: Decimal = cleaned_data.get("base_salary") or Decimal("0")
        bonus: Decimal = cleaned_data.get("production_bonus") or Decimal("0")
        deductions: Decimal = cleaned_data.get("deductions") or Decimal("0")

        # حساب صافي المرتب تلقائي
        final_salary = base_salary + bonus - deductions
        if final_salary < 0:
            raise ValidationError(_("صافي المرتب لا يمكن أن يكون أقل من صفر."))

        # ضع القيمة على الـ instance كذلك لضمان الاتساق حتى لو الحقل غير معروض في الفورم
        self.instance.final_salary = final_salary
        return cleaned_data


# ✅ نموذج إدارة لائحة الخصومات والمكافآت
PolicySettingFormSet = modelformset_factory(
    PolicySetting,
    fields=("key", "value", "description"),
    extra=0,
    widgets={
        "key": forms.TextInput(attrs={"readonly": "readonly", "class": "form-control"}),
        "value": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
        "description": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
    },
)
