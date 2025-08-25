# ERP_CORE/tracking/models.py

from django.db import models
from django.utils import timezone


class ProductTracking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الشحن'),
        ('in_transit', 'قيد النقل'),
        ('delivered', 'تم التسليم'),
        ('cancelled', 'أُلغيت')
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'نقدي'),
        ('vodafone', 'فودافون كاش'),
        ('instapay', 'إنستا باي'),
        ('bank', 'تحويل بنكي')
    ]

    product_name = models.CharField(max_length=255, verbose_name="اسم المنتج")
    tracking_code = models.CharField(max_length=100, unique=True, verbose_name="كود التتبع")
    customer_name = models.CharField(max_length=255, verbose_name="اسم العميل")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="طريقة الدفع")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="حالة الشحنة")
    shipping_company = models.CharField(max_length=100, blank=True, verbose_name="شركة الشحن")
    shipment_date = models.DateField(default=timezone.now, verbose_name="تاريخ الشحن")
    delivery_date = models.DateField(blank=True, null=True, verbose_name="تاريخ التسليم")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تتبع شحنة"
        verbose_name_plural = "تتبع الشحنات"

    def __str__(self):
        return f"{self.product_name} ({self.tracking_code})"


# ✅ موديل حركة الشحنة
class ProductTrackingMovement(models.Model):
    tracking = models.ForeignKey(
        ProductTracking,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name="الشحنة"
    )
    location = models.CharField(max_length=255, verbose_name="الموقع الحالي")
    status = models.CharField(max_length=20, choices=ProductTracking.STATUS_CHOICES, verbose_name="الحالة")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="وقت الحركة")
    note = models.TextField(blank=True, null=True, verbose_name="ملاحظة")

    class Meta:
        verbose_name = "حركة شحنة"
        verbose_name_plural = "حركات الشحنات"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.tracking.tracking_code} - {self.get_status_display()} @ {self.location}"
