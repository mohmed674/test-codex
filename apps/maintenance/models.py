from django.db import models
from apps.employees.models import Employee


class Machine(models.Model):
    STATUS_CHOICES = [
        ('operational', 'تعمل'),
        ('stopped', 'متوقفة'),
        ('maintenance', 'صيانة')
    ]

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operational')
    total_runtime_hours = models.PositiveIntegerField(default=0)
    production_line = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    def maintenance_count(self):
        return self.maintenance_logs.count()


class MaintenanceLog(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='maintenance_logs')
    description = models.TextField(blank=True)
    maintenance_date = models.DateField()
    next_maintenance = models.DateField(null=True, blank=True)
    technician = models.CharField(max_length=100, blank=True, null=True)
    issue = models.TextField(blank=True, null=True)
    action_taken = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.machine.name} - {self.maintenance_date}"

    class Meta:
        ordering = ['-maintenance_date']


# ✅ نموذج ذكي لإرسال طلب صيانة قبل التنفيذ
REQUEST_STATUS = [
    ('pending', 'قيد المراجعة'),
    ('approved', 'تمت الموافقة'),
    ('rejected', 'مرفوضة'),
    ('in_progress', 'جاري التنفيذ'),
    ('completed', 'تمت الصيانة'),
]

class MaintenanceRequest(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, verbose_name="الماكينة")
    reported_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="المبلغ")
    issue_description = models.TextField(verbose_name="وصف المشكلة")
    request_date = models.DateField(auto_now_add=True, verbose_name="تاريخ الطلب")
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='pending', verbose_name="الحالة")
    resolution_notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات التنفيذ")

    class Meta:
        verbose_name = "طلب صيانة"
        verbose_name_plural = "طلبات الصيانة"
        ordering = ['-request_date']

    def __str__(self):
        return f"طلب صيانة - {self.machine.name} - {self.get_status_display()}"
