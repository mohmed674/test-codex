from django.db import models
from apps.employees.models import Employee

class MonitoringRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'حاضر'),
        ('absent', 'غائب'),
        ('late', 'متأخر'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.status}"

class Evaluation(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='monitoring_evaluations'  # لحل التعارض مع evaluation.Evaluation
    )
    score = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f"{self.employee.name} - {self.score} - {self.date}"
