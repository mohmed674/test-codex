from django.db import models
from apps.clients.models import Client
from apps.employees.models import Employee

class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'جديد'),
        ('contacted', 'تم التواصل'),
        ('qualified', 'مهتم'),
        ('converted', 'تم التحويل'),
        ('lost', 'مفقود'),
    ]
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Interaction(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='interactions')
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField()
    by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"تواصل مع {self.lead.name} بتاريخ {self.date.strftime('%Y-%m-%d')}"

class Opportunity(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    expected_close_date = models.DateField()
    is_won = models.BooleanField(default=False)

    def __str__(self):
        return f"فرصة {self.lead.name} - {self.value} جنيه"
