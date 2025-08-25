# ERP_CORE/monitoring/models.py

from django.db import models
from django.utils import timezone


class Client(models.Model):
    name = models.CharField("اسم العميل", max_length=100)
    contact = models.CharField("وسيلة التواصل", max_length=100, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"


ORDER_STATUS_CHOICES = [
    ('Pending', 'قيد الانتظار'),
    ('Confirmed', 'تم التأكيد'),
    ('Dispatched', 'تم الإرسال'),
    ('Delivered', 'تم التسليم'),
    ('Cancelled', 'ملغي'),
]

class DistributionOrder(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="العميل")
    date = models.DateField("تاريخ الإنشاء", auto_now_add=True)
    last_updated = models.DateTimeField("آخر تعديل", auto_now=True)
    product_name = models.CharField("اسم المنتج", max_length=100)
    quantity = models.PositiveIntegerField("الكمية")
    status = models.CharField("الحالة", max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    notes = models.TextField("ملاحظات", blank=True)

    def __str__(self):
        return f"{self.client.name} - {self.product_name}"

    class Meta:
        ordering = ['-date']
        verbose_name = "طلب توزيع"
        verbose_name_plural = "طلبات التوزيع"


SHIPMENT_STATUS_CHOICES = [
    ('In Transit', 'قيد الشحن'),
    ('Delivered', 'تم التسليم'),
    ('Returned', 'مرتجع'),
    ('Lost', 'مفقود'),
    ('Delayed', 'متأخر'),
]

class Shipment(models.Model):
    tracking_number = models.CharField("رقم التتبع", max_length=100, unique=True)
    order = models.ForeignKey(DistributionOrder, on_delete=models.CASCADE, verbose_name="الطلب")
    shipped_date = models.DateField("تاريخ الشحن", default=timezone.now)
    status = models.CharField("حالة الشحنة", max_length=20, choices=SHIPMENT_STATUS_CHOICES, default='In Transit')
    location = models.CharField("آخر موقع معروف", max_length=255, blank=True)
    delivery_notes = models.TextField("ملاحظات التسليم", blank=True)

    def __str__(self):
        return f"{self.tracking_number} - {self.status}"

    class Meta:
        ordering = ['-shipped_date']
        verbose_name = "شحنة"
        verbose_name_plural = "الشحنات"
