from django.db import models
from apps.suppliers.models import Supplier
from apps.products.models import Product
from django.contrib.auth.models import User

class RFQ(models.Model):
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()

    def __str__(self):
        return self.title

class RFQItem(models.Model):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

class RFQResponse(models.Model):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

class RFQResponseItem(models.Model):
    response = models.ForeignKey(RFQResponse, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time_days = models.PositiveIntegerField()
