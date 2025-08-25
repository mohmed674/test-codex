from django.db import models
from apps.clients.models import Client
from apps.sales.models import SaleInvoice  # ← التعديل هنا فقط
from apps.accounting.models import PaymentMethod

class ShippingCompany(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('created', 'تم الإنشاء'),
        ('in_transit', 'قيد التوصيل'),
        ('delivered', 'تم التسليم'),
        ('failed', 'فشل التوصيل'),
    ]

    invoice = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE)  # ← هنا برضه
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    company = models.ForeignKey(ShippingCompany, on_delete=models.SET_NULL, null=True)
    tracking_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    shipping_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"شحنة {self.tracking_number} - {self.get_status_display()}"
