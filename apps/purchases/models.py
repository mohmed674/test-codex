# ERP_CORE/purchases/models.py

from django.db import models
from apps.employees.models import Employee
from apps.departments.models import Department
from apps.products.models import Product
from apps.accounting.models import Account
from django.utils import timezone


class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'موافق عليه'),
        ('rejected', 'مرفوض'),
        ('ordered', 'تم الطلب'),
        ('received', 'تم الاستلام'),
    ]

    requested_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    purpose = models.TextField(verbose_name="الغرض من الطلب")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"طلب شراء {self.id} من {self.department.name}"


class PurchaseItem(models.Model):
    request = models.ForeignKey(PurchaseRequest, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class PurchaseOrder(models.Model):
    purchase_request = models.OneToOneField(PurchaseRequest, on_delete=models.CASCADE)
    supplier_name = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    order_date = models.DateField(default=timezone.now)
    expected_delivery = models.DateField(null=True, blank=True)
    is_delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"أمر شراء #{self.id} - {self.supplier_name}"


class PurchaseInvoice(models.Model):
    order = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100, unique=True)
    invoice_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"فاتورة #{self.invoice_number}"
