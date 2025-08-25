from django import forms
from django.utils.translation import gettext_lazy as _
from .models import SaleInvoice, SaleItem, SalesPerformance, SmartSalesSuggestion

# ✅ نموذج إنشاء الفاتورة
class SaleInvoiceForm(forms.ModelForm):
    class Meta:
        model = SaleInvoice
        fields = ['invoice_number', 'client', 'date', 'payment_method']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'invoice_number': _('رقم الفاتورة'),
            'client': _('العميل'),
            'date': _('تاريخ الفاتورة'),
            'payment_method': _('طريقة الدفع'),
        }


# ✅ نموذج بند الفاتورة
class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['invoice', 'product', 'quantity', 'unit_price', 'discount']
        labels = {
            'invoice': _('الفاتورة'),
            'product': _('المنتج'),
            'quantity': _('الكمية'),
            'unit_price': _('سعر الوحدة'),
            'discount': _('الخصم'),
        }


# ✅ نموذج أداء مندوبي المبيعات
class SalesPerformanceForm(forms.ModelForm):
    class Meta:
        model = SalesPerformance
        fields = ['employee', 'date', 'sales_total']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'employee': _('الموظف'),
            'date': _('التاريخ'),
            'sales_total': _('إجمالي المبيعات'),
        }


# ✅ نموذج اقتراحات ذكية
class SmartSalesSuggestionForm(forms.ModelForm):
    class Meta:
        model = SmartSalesSuggestion
        fields = ['product', 'suggested_action']
        labels = {
            'product': _('المنتج'),
            'suggested_action': _('الاقتراح'),
        }
