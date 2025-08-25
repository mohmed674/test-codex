from django.db import models
from datetime import timedelta

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Employee(models.Model):
    GENDER_CHOICES = (
        ('M', 'ذكر'),
        ('F', 'أنثى'),
    )

    name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    department = models.ForeignKey('departments.Department', on_delete=models.SET_NULL, null=True, related_name='employees')
    national_id = models.CharField(max_length=14, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)

    total_rewards = models.PositiveIntegerField(default=0)
    total_deductions = models.PositiveIntegerField(default=0)
    total_warnings = models.PositiveIntegerField(default=0)
    total_evaluations = models.PositiveIntegerField(default=0)
    evaluation_score = models.FloatField(default=0.0)
    behavior_status = models.CharField(max_length=50, default='جيد')

    def __str__(self):
        return self.name

    def hourly_rate(self):
        return (self.salary / 30) / 8 if hasattr(self, 'salary') and self.salary else 0

    def daily_production_value(self):
        return 200  # ثابت مؤقت


class AttendanceRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employees_attendance_records')
    date = models.DateField()
    check_in = models.TimeField(blank=True, null=True)
    is_absent = models.BooleanField(default=False)
    is_excused_absence = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee.name} - {self.date}"


class MonthlyIncentive(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employees_monthly_incentives')
    month = models.DateField()
    commitment_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quarterly_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    penalty_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('employee', 'month')

    def __str__(self):
        return f"{self.employee.name} - {self.month.strftime('%m/%Y')}"
