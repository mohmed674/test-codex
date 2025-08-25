from django.db import models
from apps.products.models import Product
from apps.clients.models import Client
from apps.employees.models import Employee
from apps.accounting.models import PaymentMethod

class POSSession(models.Model):
    name = models.CharField(max_length=100)
    cashier = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.cashier}"

class POSOrder(models.Model):
    session = models.ForeignKey(POSSession, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    is_refunded = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - {self.total} EGP"

class POSOrderItem(models.Model):
    order = models.ForeignKey(POSOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.unit_price
