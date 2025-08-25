from django.db import models
from apps.employees.models import Employee
from apps.clients.models import Client
from apps.suppliers.models import Supplier

class LegalCase(models.Model):
    CASE_STATUS_CHOICES = [
        ('open', 'مفتوحة'),
        ('investigation', 'قيد التحقيق'),
        ('judged', 'صدر حكم'),
        ('closed', 'مغلقة'),
    ]

    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=CASE_STATUS_CHOICES, default='open')
    related_client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    related_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    related_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    court_name = models.CharField(max_length=150, blank=True, null=True)
    session_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    lawyer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='legal_cases')
    attachment = models.FileField(upload_to='legal/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
