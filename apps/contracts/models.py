from django.db import models
from apps.clients.models import Client
from apps.suppliers.models import Supplier
from apps.employees.models import Employee

class Contract(models.Model):
    CONTRACT_TYPE_CHOICES = [
        ('client', 'عميل'),
        ('supplier', 'مورد'),
        ('employee', 'موظف'),
        ('custom', 'اتفاقية خاصة'),
    ]

    title = models.CharField(max_length=200)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES)
    related_client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    related_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    related_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='contracts/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.get_contract_type_display()}"
