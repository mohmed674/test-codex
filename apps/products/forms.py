# ERP_CORE/products/forms.py

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import FinishedProduct


class FinishedProductForm(forms.ModelForm):
    """
    يحافظ على الحقول الأصلية ويضيف توسعات اختيارية بما يتوافق مع الموديل.
    لا يحذف أي منطق قائم.
    """

    class Meta:
        model = FinishedProduct
        fields = [
            # الحقول الأصلية
            'inventory_item',
            'product_code',
            'name',
            'quantity',
            'date_produced',
            'image',
            'quality_status',
            'expiration_date',

            # توسعات اختيارية متاحة في الموديل
            'batch_number',
            'lot',
            'location_code',
            'notes',
            'attributes',
        ]
        labels = {
            'inventory_item': _("الصنف المرتبط"),
            'product_code': _("كود المنتج"),
            'name': _("اسم المنتج"),
            'quantity': _("الكمية"),
            'date_produced': _("تاريخ الإنتاج"),
            'image': _("صورة المنتج"),
            'quality_status': _("حالة الجودة"),
            'expiration_date': _("تاريخ الانتهاء (اختياري)"),
            'batch_number': _("رقم التشغيل/الدفعة"),
            'lot': _("LOT"),
            'location_code': _("موقع التخزين (رمز)"),
            'notes': _("ملاحظات"),
            'attributes': _("خصائص/سمات (JSON)"),
        }
        help_texts = {
            'product_code': _("قيمة فريدة تستخدم في التتبع والـ QR."),
            'quantity': _("أدخل رقمًا موجبًا."),
            'attributes': _('مثال: {"color":"black","size":"M"}'),
        }
        widgets = {
            'date_produced': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
            'quality_status': forms.Select(),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'attributes': forms.Textarea(attrs={'rows': 4, 'dir': 'ltr'}),
            'quantity': forms.NumberInput(attrs={'min': 0}),
        }
        error_messages = {
            'product_code': {
                'unique': _("هذا الكود مستخدم بالفعل."),
                'required': _("يرجى إدخال كود المنتج."),
            },
            'name': {'required': _("يرجى إدخال اسم المنتج.")},
            'quantity': {'invalid': _("قيمة غير صحيحة.")},
        }

    def clean_product_code(self):
        code = (self.cleaned_data.get('product_code') or '').strip()
        return code

    def clean(self):
        cleaned = super().clean()

        # تحقق منطقي: تاريخ الانتهاء ≥ تاريخ الإنتاج
        date_produced = cleaned.get('date_produced')
        expiration_date = cleaned.get('expiration_date')
        if expiration_date and date_produced and expiration_date < date_produced:
            self.add_error('expiration_date', _("تاريخ الانتهاء يجب أن يكون بعد/يساوي تاريخ الإنتاج."))

        # الكمية ≥ 0
        qty = cleaned.get('quantity')
        try:
            if qty is not None and float(qty) < 0:
                self.add_error('quantity', _("الكمية يجب أن تكون رقمًا موجبًا."))
        except Exception:
            self.add_error('quantity', _("قيمة غير صحيحة للكمية."))

        return cleaned
