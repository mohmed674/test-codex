from django.db import models
from apps.clients.models import Client
from apps.employees.models import Employee
from apps.sales.models import SaleInvoice  # ← هنا التعديل

class SupportTicket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'منخفضة'),
        ('medium', 'متوسطة'),
        ('high', 'مرتفعة'),
    ]

    STATUS_CHOICES = [
        ('open', 'مفتوح'),
        ('in_progress', 'قيد التنفيذ'),
        ('resolved', 'تم الحل'),
        ('closed', 'مغلق'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    invoice = models.ForeignKey(SaleInvoice, on_delete=models.SET_NULL, null=True, blank=True)  # ← هنا التعديل
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"طلب دعم #{self.id} - {self.title}"


class SupportResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"رد على تذكرة #{self.ticket.id} في {self.created_at.strftime('%Y-%m-%d')}"
