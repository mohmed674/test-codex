from django.db import models
from apps.employees.models import Employee

class Evaluation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    attendance_score = models.IntegerField(default=0)
    productivity_score = models.IntegerField(default=0)
    behavior_score = models.IntegerField(default=0)
    final_score = models.FloatField(default=0)
    notes = models.TextField(blank=True)

    def calculate_final_score(self):
        self.final_score = round((self.attendance_score + self.productivity_score + self.behavior_score) / 3, 2)
        return self.final_score

    def save(self, *args, **kwargs):
        self.calculate_final_score()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"تقييم {self.employee.name} بتاريخ {self.date}"


class LatenessAbsence(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    is_late = models.BooleanField(default=False)
    is_absent = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        status = []
        if self.is_late:
            status.append("تأخير")
        if self.is_absent:
            status.append("غياب")
        return f"{self.employee.name} - {self.date} - {' و '.join(status) or 'حضور'}"
