from typing import Any, Dict, Iterable, Optional, Tuple, cast

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import ReportLog, RiskIncident

User = get_user_model()


# ============================ Helpers ============================


class BaseStyledModelForm(forms.ModelForm):
    """
    Enterprise-grade base form:
    - adds 'form-control' classes automatically
    - provides common date/time widgets
    - localized, typed clean hooks
    """

    DATE_INPUT_FORMATS: Tuple[str, ...] = ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d")
    DATETIME_INPUT_FORMATS: Tuple[str, ...] = (
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M",
        "%Y/%m/%d %H:%M",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # Keep admin/widgets styles intact
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css} form-control".strip()
            # Add placeholder as label by default
            field.widget.attrs.setdefault("placeholder", str(field.label or name))

    @staticmethod
    def date_widget() -> forms.DateInput:
        return forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")

    @staticmethod
    def datetime_widget() -> forms.DateTimeInput:
        return forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        )


# ============================ Forms ============================


class RiskIncidentForm(BaseStyledModelForm):
    """
    إدارة بلّغات/حوادث المخاطر:
    - تحققات ذكية للمدخلات
    - واجهات مستخدم محسّنة
    """

    class Meta:
        model = RiskIncident
        fields = "__all__"
        widgets = {
            # إن كان الحقل موجودًا بالموديل
            "notes": forms.Textarea(attrs={"rows": 3}),
            "reported_at": BaseStyledModelForm.datetime_widget(),
        }

    def clean_user(self) -> Any:
        # self.cleaned_data قد يُرى كـ Optional في بعض المحللات الساكنة
        data = cast(Dict[str, Any], self.cleaned_data)
        user = data.get("user")
        # السماح بـ None لكن امنع مستخدم غير موجود/غير نشط بوضوح
        if user and not getattr(user, "is_active", True):
            raise ValidationError(_("المستخدم المحدد غير نشط."))
        return user

    def clean(self) -> Dict[str, Any]:
        cleaned = cast(Dict[str, Any], super().clean())
        category = (cleaned.get("category") or "").strip()
        event_type = (cleaned.get("event_type") or "").strip()
        if not category and not event_type:
            raise ValidationError(
                _("يجب تحديد 'الفئة' أو 'نوع الحدث' على الأقل لوصف الحادثة.")
            )
        return cleaned


class ReportLogForm(BaseStyledModelForm):
    """
    سجل الإجراءات/التقارير:
    - توحيد الحقول المرجعية وتضمين ملاحظات مختصرة
    """

    class Meta:
        model = ReportLog
        fields = "__all__"
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "timestamp": BaseStyledModelForm.datetime_widget(),
        }

    def clean_ref(self) -> str:
        data = cast(Dict[str, Any], self.cleaned_data)
        ref = (data.get("ref") or "").strip()
        if not ref:
            raise ValidationError(_("المرجع مطلوب للتتبع."))
        if len(ref) > 128:
            raise ValidationError(_("طول المرجع يجب ألا يتجاوز 128 حرفًا."))
        return ref


# ======================= Search / Filter Forms =======================


class RiskIncidentFilterForm(forms.Form):
    """
    نموذج فلترة/بحث لحوادث المخاطر على مستوى الإنتاج:
    - q: نص حر للبحث في الملاحظات/الحدث/الفئة
    - الفترة الزمنية
    - مستوى الخطورة والفئة
    - المستخدم
    """

    q = forms.CharField(
        label=_("بحث"),
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("نص حر")}
        ),
    )
    category = forms.CharField(
        label=_("الفئة"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    risk_level = forms.ChoiceField(
        label=_("مستوى الخطورة"),
        required=False,
        choices=[("", _("الكل"))]
        + [(lvl, lvl) for lvl in ("LOW", "MEDIUM", "HIGH", "CRITICAL")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    user = forms.ModelChoiceField(
        label=_("المستخدم"),
        required=False,
        queryset=User.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date_from = forms.DateField(
        label=_("من تاريخ"),
        required=False,
        widget=BaseStyledModelForm.date_widget(),
        input_formats=BaseStyledModelForm.DATE_INPUT_FORMATS,
    )
    date_to = forms.DateField(
        label=_("إلى تاريخ"),
        required=False,
        widget=BaseStyledModelForm.date_widget(),
        input_formats=BaseStyledModelForm.DATE_INPUT_FORMATS,
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # تحميل المستخدمين المؤهلين فقط (نشطون)
        user_field = cast(forms.ModelChoiceField, self.fields["user"])
        user_field.queryset = User.objects.filter(is_active=True).order_by("username")

    def cleaned_period(self) -> Tuple[Optional[str], Optional[str]]:
        """إرجاع الفترة الزمنية بصيغة ISO YYYY-MM-DD (آمنة للاستخدام في الـ templates)."""
        df = self.cleaned_data.get("date_from")
        dt = self.cleaned_data.get("date_to")
        return (df.isoformat() if df else None, dt.isoformat() if dt else None)


class ReportLogFilterForm(forms.Form):
    """
    نموذج فلترة لسجل التقارير:
    - model, action, ref, الفترة الزمنية
    """

    model = forms.CharField(
        label=_("الموديل"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    action = forms.CharField(
        label=_("الإجراء"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    ref = forms.CharField(
        label=_("المرجع"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    date_from = forms.DateField(
        label=_("من تاريخ"),
        required=False,
        widget=BaseStyledModelForm.date_widget(),
        input_formats=BaseStyledModelForm.DATE_INPUT_FORMATS,
    )
    date_to = forms.DateField(
        label=_("إلى تاريخ"),
        required=False,
        widget=BaseStyledModelForm.date_widget(),
        input_formats=BaseStyledModelForm.DATE_INPUT_FORMATS,
    )


# ======================= Bulk & Utility Forms =======================


class BulkRiskLevelForm(forms.Form):
    """
    نموذج تحديث جماعي لمستوى الخطورة.
    يستقبل قائمة معرفات للحوادث ويضبط مستوى الخطورة المحدد.
    """

    incident_ids = forms.CharField(widget=forms.HiddenInput())
    risk_level = forms.ChoiceField(
        label=_("مستوى الخطورة"),
        choices=[(lvl, lvl) for lvl in ("LOW", "MEDIUM", "HIGH", "CRITICAL")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def parse_ids(self) -> Iterable[int]:
        raw = (self.cleaned_data.get("incident_ids") or "").strip()
        ids: list[int] = []
        for part in raw.split(","):
            part = part.strip()
            if part.isdigit():
                ids.append(int(part))
        return ids

    def apply(self) -> int:
        """
        يطبّق التحديث الجماعي ويعيد عدد السجلات المحدثة.
        الاستخدام:
            if form.is_valid(): updated = form.apply()
        """
        ids = list(self.parse_ids())
        level = self.cleaned_data["risk_level"]
        if not ids:
            return 0
        return RiskIncident.objects.filter(id__in=ids).update(risk_level=level)
