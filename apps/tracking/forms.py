from django import forms
from .models import ProductTracking, ProductTrackingMovement


class ProductTrackingForm(forms.ModelForm):
    class Meta:
        model = ProductTracking
        fields = [
            'product_name',
            'tracking_code',
            'customer_name',
            'payment_method',
            'status',
            'shipping_company',
            'shipment_date',
            'delivery_date',
            'notes',
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tracking_code': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'shipping_company': forms.TextInput(attrs={'class': 'form-control'}),
            'shipment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'product_name': 'اسم المنتج',
            'tracking_code': 'كود التتبع',
            'customer_name': 'اسم العميل',
            'payment_method': 'طريقة الدفع',
            'status': 'حالة الشحنة',
            'shipping_company': 'شركة الشحن',
            'shipment_date': 'تاريخ الشحن',
            'delivery_date': 'تاريخ التسليم',
            'notes': 'ملاحظات إضافية',
        }
        help_texts = {
            'tracking_code': 'أدخل كود تتبع فريد للشحنة.',
            'delivery_date': 'اتركه فارغًا إذا لم يتم التسليم بعد.',
        }


class ProductTrackingMovementForm(forms.ModelForm):
    class Meta:
        model = ProductTrackingMovement
        fields = ['tracking', 'location', 'status', 'timestamp']
        widgets = {
            'tracking': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'timestamp': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
        labels = {
            'tracking': 'الشحنة المرتبطة',
            'location': 'الموقع الحالي',
            'status': 'الحالة',
            'timestamp': 'وقت الحركة',
        }
        help_texts = {
            'status': 'اختر الحالة الحالية بناءً على موقع الشحنة.',
            'timestamp': 'يمكنك ترك الوقت الحالي تلقائيًا أو تغييره يدويًا.',
        }

        
