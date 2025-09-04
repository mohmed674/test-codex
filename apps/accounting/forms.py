from decimal import Decimal
from typing import Any, Dict, Type, TYPE_CHECKING, cast

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import (
    Invoice,
    InvoiceItem,
    JournalEntry,
    JournalItem,
    PurchaseInvoice,
    SalesInvoice,
)

# ملاحظة مهمة:
# استخدام Generics مثل forms.ModelForm[Model] يسبب خطأ وقت التشغيل في Django 4.2
# ("ModelFormMetaclass object is not subscriptable").
# لذلك نستخدم forms.ModelForm العادي، ونستعمل cast داخل clean() فقط للـ typing.

# ================= قيد اليومية =================
class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ["date", "description", "debit", "credit", "invoice"]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "placeholder": "اختر التاريخ",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "form-control",
                    "placeholder": "أدخل وصف القيد",
                }
            ),
            "debit": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "أدخل المبلغ المدين",
                }
            ),
            "credit": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "أدخل المبلغ الدائن",
                }
            ),
            "invoice": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "date": "تاريخ القيد",
            "description": "الوصف التفصيلي",
            "debit": "المبلغ المدين",
            "credit": "المبلغ الدائن",
            "invoice": "فاتورة مرتبطة (إن وجدت)",
        }

    def clean_description(self) -> str:
        desc = (self.cleaned_data.get("description") or "").strip()
        if len(desc) < 3:
            raise ValidationError("الوصف مطلوب ويجب أن يكون مفصلًا")
        return desc

    def clean(self) -> Dict[str, Any]:
        cleaned = cast(Dict[str, Any], super().clean())
        debit = Decimal(cleaned.get("debit") or 0)
        credit = Decimal(cleaned.get("credit") or 0)
        invalid_zero = debit == 0 and credit == 0
        invalid_both = debit > 0 and credit > 0
        if invalid_zero or invalid_both:
            raise ValidationError(
                "يجب أن يكون إما مبلغ مدين أو مبلغ دائن فقط "
                "(ولا يمكن أن يكونا صفرًا معًا)."
            )
        return cleaned


class JournalItemForm(forms.ModelForm):
    class Meta:
        model = JournalItem
        fields = ["account", "debit", "credit"]
        widgets = {
            "account": forms.Select(attrs={"class": "form-control"}),
            "debit": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "مدين"}
            ),
            "credit": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "دائن"}
            ),
        }
        labels = {
            "account": "اسم الحساب",
            "debit": "مدين",
            "credit": "دائن",
        }


# inlineformset_factory يُرجِع "كلاس" فورم-ست؛ نصرّح بالنوع Type[BaseInlineFormSet] لتوافق الأدوات.
JournalItemFormSet: Type[BaseInlineFormSet] = inlineformset_factory(
    parent_model=JournalEntry,
    model=JournalItem,
    form=JournalItemForm,
    extra=1,
    can_delete=True,
)


class JournalEntrySearchForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="من تاريخ",
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="إلى تاريخ",
    )
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "بحث عن وصف القيد...",
            }
        ),
        label="بحث بالوصف",
    )


# ================= الفواتير العامة =================
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["customer", "date_issued", "payment_method", "sale_type"]
        widgets = {
            "customer": forms.Select(attrs={"class": "form-select"}),
            "date_issued": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "sale_type": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "customer": "العميل",
            "date_issued": "تاريخ الفاتورة",
            "payment_method": "طريقة الدفع",
            "sale_type": "نوع البيع",
        }

    def clean(self) -> Dict[str, Any]:
        cleaned = cast(Dict[str, Any], super().clean())
        if not cleaned.get("customer"):
            raise ValidationError("الرجاء اختيار العميل.")
        return cleaned


# ================= فواتير المبيعات =================
class SalesInvoiceForm(forms.ModelForm):
    class Meta:
        model = SalesInvoice
        exclude = ("created_by", "created_at", "total_amount")
        widgets = {
            "number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "اتركه فارغًا للترقيم التلقائي",
                }
            ),
            "customer": forms.Select(attrs={"class": "form-select"}),
            "date_issued": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "due_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "number": "رقم الفاتورة",
            "customer": "العميل",
            "date_issued": "تاريخ الفاتورة",
            "due_date": "تاريخ الاستحقاق",
            "status": "الحالة",
        }

    def clean(self) -> Dict[str, Any]:
        cleaned = cast(Dict[str, Any], super().clean())
        date_issued = cleaned.get("date_issued")
        due_date = cleaned.get("due_date")
        if date_issued and due_date and due_date < date_issued:
            raise ValidationError("تاريخ الاستحقاق يجب أن يكون بعد تاريخ الإصدار.")
        return cleaned


# ================= فواتير المشتريات =================
class PurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoice
        exclude = ("created_by", "created_at", "total_amount")
        widgets = {
            "number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "اتركه فارغًا للترقيم التلقائي",
                }
            ),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "date_issued": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "due_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"})
            ,
            "status": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "number": "رقم الفاتورة",
            "supplier": "المورد",
            "date_issued": "تاريخ الفاتورة",
            "due_date": "تاريخ الاستحقاق",
            "status": "الحالة",
        }

    def clean(self) -> Dict[str, Any]:
        cleaned = cast(Dict[str, Any], super().clean())
        date_issued = cleaned.get("date_issued")
        due_date = cleaned.get("due_date")
        if date_issued and due_date and due_date < date_issued:
            raise ValidationError("تاريخ الاستحقاق يجب أن يكون بعد تاريخ الإصدار.")
        return cleaned


# ================= بنود الفاتورة =================
class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        # يحددها الـ formset حسب سياق الفاتورة
        exclude = ("sales_invoice", "purchase_invoice")
        widgets = {
            "product_name": forms.TextInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }
        labels = {
            "product_name": "اسم المنتج",
            "quantity": "الكمية",
            "unit_price": "سعر الوحدة",
            "notes": "ملاحظات",
        }

    def clean(self) -> Dict[str, Any]:
        cleaned = cast(Dict[str, Any], super().clean())
        qty = int(cleaned.get("quantity") or 0)
        price = Decimal(cleaned.get("unit_price") or 0)
        if qty <= 0:
            raise ValidationError("الكمية يجب أن تكون أكبر من صفر.")
        if price < 0:
            raise ValidationError("سعر الوحدة لا يمكن أن يكون سالبًا.")
        return cleaned
