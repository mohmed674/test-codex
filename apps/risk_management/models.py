from django.db import models
from django.contrib.auth import get_user_model

class Risk(models.Model):
    RISK_TYPE_CHOICES = [
        ('operational', 'تشغيلي'),
        ('financial', 'مالي'),
        ('supply', 'سلاسل التوريد'),
        ('legal', 'قانوني'),
        ('other', 'أخرى'),
    ]
    SEVERITY_CHOICES = [
        ('low', 'منخفض'),
        ('medium', 'متوسط'),
        ('high', 'مرتفع'),
        ('critical', 'حرج'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    risk_type = models.CharField(max_length=50, choices=RISK_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    probability = models.IntegerField(help_text="احتمالية حدوث الخطر (1-100)")
    mitigation_plan = models.TextField(blank=True)
    reported_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-reported_at']

    def __str__(self):
        return self.title
