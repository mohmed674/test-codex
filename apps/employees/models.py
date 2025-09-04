from decimal import Decimal

from django.db import models


class Department(models.Model):
    """قسم وظيفي داخل المؤسسة."""

    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]


class Employee(models.Model):
    """موظف داخل المؤسسة."""

    GENDER_CHOICES = (
        ("M", "ذكر"),
        ("F", "أنثى"),
    )

    name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="M")
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.SET_NULL,
        null=True,
        related_name="employees",
    )
    national_id = models.CharField(max_length=14, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)

    total_rewards = models.PositiveIntegerField(default=0)
    total_deductions = models.PositiveIntegerField(default=0)
    total_warnings = models.PositiveIntegerField(default=0)
    total_evaluations = models.PositiveIntegerField(default=0)
    evaluation_score = models.FloatField(default=0.0)
    behavior_status = models.CharField(max_length=50, default="جيد")

    def __str__(self) -> str:
        return self.name

    def hourly_rate(self) -> float:
        """تقدير معدل الأجر بالساعة إن وُجد راتب مرتبط بالموظف."""
        salary = getattr(self, "salary", 0) or 0  # قد يُحقن من payroll
        try:
            s = float(salary)
        except Exception:
            s = 0.0
        return (s / 30.0) / 8.0 if s else 0.0

    def daily_production_value(self) -> int:
        """قيمة إنتاج يومية تقديرية (ثابت مؤقت حتى تتكامل مع الإنتاج)."""
        return 200

    class Meta:
        verbose_name = "موظف"
        verbose_name_plural = "الموظفون"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["active"]),
            models.Index(fields=["national_id"]),
        ]


class AttendanceRecord(models.Model):
    """سجل حضور الموظف."""

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="employees_attendance_records"
    )
    date = models.DateField()
    check_in = models.TimeField(blank=True, null=True)
    is_absent = models.BooleanField(default=False)
    is_excused_absence = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.employee.name} - {self.date}"

    class Meta:
        verbose_name = "حضور"
        verbose_name_plural = "سجلات الحضور"
        ordering = ["-date"]
        indexes = [models.Index(fields=["date"]), models.Index(fields=["employee"])]


class MonthlyIncentive(models.Model):
    """حوافز شهرية مرتبطة بموظف."""

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="employees_monthly_incentives"
    )
    month = models.DateField()
    commitment_bonus = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )
    quarterly_bonus = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )
    penalty_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )

    class Meta:
        unique_together = ("employee", "month")
        verbose_name = "حافز شهري"
        verbose_name_plural = "حوافز شهرية"
        ordering = ["-month"]
        indexes = [models.Index(fields=["month"]), models.Index(fields=["employee"])]

    def __str__(self) -> str:
        return f"{self.employee.name} - {self.month.strftime('%m/%Y')}"
