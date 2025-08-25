from django.db import models

class WhatsAppOrder(models.Model):
    customer_phone = models.CharField(max_length=20)
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, default="New")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_phone} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
