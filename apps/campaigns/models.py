from django.db import models
from apps.clients.models import Client
from apps.employees.models import Employee

class Campaign(models.Model):
    CHANNEL_CHOICES = [
        ('email', 'بريد إلكتروني'),
        ('sms', 'رسالة نصية'),
        ('whatsapp', 'واتساب'),
    ]

    name = models.CharField(max_length=150)
    content = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    scheduled_date = models.DateTimeField()
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class CampaignTarget(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='targets')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    is_delivered = models.BooleanField(default=False)
    response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.client} - {self.campaign.name}"
