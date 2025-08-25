from django.db import models
from django.utils import timezone
from apps.accounting.models import SupplierInvoice
from apps.employees.models import Employee

class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم المورد")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, null=True, verbose_name="البريد الإلكتروني")
    address = models.TextField(blank=True, null=True, verbose_name="العنوان")
    governorate = models.CharField(max_length=100, blank=True, null=True, verbose_name="المحافظة")
    supplier_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="نوع المورد")
    status = models.CharField(max_length=20, choices=[('active','نشط'),('inactive','غير نشط')], default='active', verbose_name="الحالة")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="أنشأ بواسطة")
    created_at = models.DateTimeField(auto_now_add=True)

    def total_invoices(self):
        return SupplierInvoice.objects.filter(supplier=self).count()

    def total_payments(self):
        return SupplierInvoice.objects.filter(supplier=self, status='paid').aggregate(models.Sum('total_amount'))['total_amount__sum'] or 0

    def __str__(self):
        return self.name
