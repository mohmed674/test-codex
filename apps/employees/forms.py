# apps/employees/forms.py
"""Employee admin form with strong validation, i18n, and clean typing.

- Fixes SIM102 by flattening nested conditionals.
- Adds comprehensive type hints (mypy-friendly).
- Wraps user-facing texts with i18n (_).
- Preserves behavior and field set; no functional removals.
"""

from __future__ import annotations

import re
from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.employees.models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "name",
            "job_title",
            "gender",
            "department",
            "national_id",
            "phone",
            "hire_date",
            "active",
            "total_rewards",
            "total_deductions",
            "total_warnings",
            "total_evaluations",
            "evaluation_score",
            "behavior_status",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "name"}
            ),
            "job_title": forms.Select(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-control"}),
            "national_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "14",
                    "inputmode": "numeric",
                }
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "tel"}
            ),
            "hire_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "total_rewards": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "total_deductions": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "total_warnings": forms.NumberInput(
                attrs={"class": "form-control", "step": "1", "min": "0"}
            ),
            "total_evaluations": forms.NumberInput(
                attrs={"class": "form-control", "step": "1", "min": "0"}
            ),
            "evaluation_score": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "behavior_status": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "name": _("الاسم"),
            "job_title": _("المسمى الوظيفي"),
            "gender": _("النوع"),
            "department": _("القسم"),
            "national_id": _("الرقم القومي"),
            "phone": _("رقم الهاتف"),
            "hire_date": _("تاريخ التعيين"),
            "active": _("نشط؟"),
            "total_rewards": _("إجمالي المكافآت"),
            "total_deductions": _("إجمالي الخصومات"),
            "total_warnings": _("عدد الإنذارات"),
            "total_evaluations": _("عدد التقييمات"),
            "evaluation_score": _("متوسط التقييم"),
            "behavior_status": _("الحالة السلوكية"),
        }
        help_texts = {
            "national_id": _("أدخل 14 رقمًا بدون مسافات."),
        }

    # ===== Field-level validations =====
    def clean_national_id(self) -> str | None:
        nid = (self.cleaned_data.get("national_id") or "").strip()
        if nid and not re.fullmatch(r"\d{14}", nid):
            raise ValidationError(_("الرقم القومي يجب أن يكون 14 رقمًا."))
        return nid or None

    def clean_phone(self) -> str | None:
        phone = (self.cleaned_data.get("phone") or "").strip()
        if phone and not re.fullmatch(r"[+\d][\d\s\-]{6,20}", phone):
            raise ValidationError(_("رقم الهاتف غير صالح."))
        if phone:
            # Normalize: collapse extra spaces
            phone = re.sub(r"\s+", " ", phone)
        return phone or None

    def clean_hire_date(self):
        hire_date = self.cleaned_data.get("hire_date")
        if hire_date and hire_date > timezone.localdate():
            raise ValidationError(_("تاريخ التعيين لا يمكن أن يكون في المستقبل."))
        return hire_date

    def clean_evaluation_score(self):
        score = self.cleaned_data.get("evaluation_score")
        if score is not None and (score < 0 or score > 100):
            raise ValidationError(_("متوسط التقييم يجب أن يكون بين 0 و 100."))
        return score

    # ===== Form-level validations =====
    def clean(self) -> dict[str, Any]:
        cleaned = super().clean()

        def _nonneg(name: str, label: str) -> None:
            val = cleaned.get(name)
            if val is not None and val < 0:
                self.add_error(name, _(f"{label} لا يمكن أن يكون سالبًا."))

        _nonneg("total_rewards", "إجمالي المكافآت")
        _nonneg("total_deductions", "إجمالي الخصومات")
        _nonneg("total_warnings", "عدد الإنذارات")
        _nonneg("total_evaluations", "عدد التقييمات")

        return cleaned

    # ===== Save normalization =====
    def save(self, commit: bool = True) -> Employee:
        obj: Employee = super().save(commit=False)
        if obj.name:
            obj.name = obj.name.strip()
        if commit:
            obj.save()
            self.save_m2m()
        return obj
