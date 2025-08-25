from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import (
    Invoice, JournalEntry, JournalItem,
    SalesInvoice, PurchaseInvoice, InvoiceItem
)

# ================= قيد اليومية =================
class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['date', 'description', 'debit', 'credit', 'invoice']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'اختر التاريخ'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'أدخل وصف القيد'}),
            'debit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'أدخل المبلغ المدين'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'أدخل المبلغ الدائن'}),
            'invoice': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'date': 'تاريخ القيد',
            'description': 'الوصف التفصيلي',
            'debit': 'المبلغ المدين',
            'credit': 'المبلغ الدائن',
            'invoice': 'فاتورة مرتبطة (إن وجدت)',
        }

    def clean_description(self):
        desc = self.cleaned_data.get('description')
        if not desc or len(desc.strip()) < 3:
            raise ValidationError("الوصف مطلوب ويجب أن يكون مفصلًا")
        return desc


class JournalItemForm(forms.ModelForm):
    class Meta:
        model = JournalItem
        fields = ['account', 'debit', 'credit']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-control'}),
            'debit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مدين'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'دائن'}),
        }
        labels = {
            'account': 'اسم الحساب',
            'debit': 'مدين',
            'credit': 'دائن',
        }


JournalItemFormSet = inlineformset_factory(
    JournalEntry,
    JournalItem,
    form=JournalItemForm,
    extra=1,
    can_delete=True
)


class JournalEntrySearchForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="من تاريخ"
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="إلى تاريخ"
    )
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'بحث عن وصف القيد...'}),
        label="بحث بالوصف"
    )


# ================= الفواتير العامة =================
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'date_issued', 'payment_method', 'sale_type']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'date_issued': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'sale_type': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'customer': 'العميل',
            'date_issued': 'تاريخ الفاتورة',
            'payment_method': 'طريقة الدفع',
            'sale_type': 'نوع البيع',
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('customer'):
            raise ValidationError("الرجاء اختيار العميل.")
        return cleaned_data


# ================= فواتير المبيعات =================
class SalesInvoiceForm(forms.ModelForm):
    class Meta:
        model = SalesInvoice
        exclude = ('created_by', 'created_at', 'total_amount')  # نستبعد المحسوبة
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اتركه فارغًا للترقيم التلقائي'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'date_issued': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'number': 'رقم الفاتورة',
            'customer': 'العميل',
            'date_issued': 'تاريخ الفاتورة',
            'due_date': 'تاريخ الاستحقاق',
            'status': 'الحالة',
        }


# ================= فواتير المشتريات =================
class PurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoice
        exclude = ('created_by', 'created_at', 'total_amount')  # نستبعد المحسوبة
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اتركه فارغًا للترقيم التلقائي'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'date_issued': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'number': 'رقم الفاتورة',
            'supplier': 'المورد',
            'date_issued': 'تاريخ الفاتورة',
            'due_date': 'تاريخ الاستحقاق',
            'status': 'الحالة',
        }


# ================= بنود الفاتورة =================
class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        exclude = ('sales_invoice', 'purchase_invoice')  # يحددها الـ formset
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'product_name': 'اسم المنتج',
            'quantity': 'الكمية',
            'unit_price': 'سعر الوحدة',
            'notes': 'ملاحظات',
        }
