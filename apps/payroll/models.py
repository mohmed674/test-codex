# apps/payroll/models.py
# ERP_CORE/payroll/models.py

from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from weasyprint import HTML  # type: ignore[import]

from apps.employees.models import Employee
from apps.evaluation.models import Evaluation


class Salary(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="payroll_salaries"
    )
    month = models.IntegerField(help_text=_("Month number (1-12)"))
    year = models.IntegerField(help_text=_("Four-digit year"))
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    production_bonus = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )
    deductions = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )
    final_salary = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to="salaries/", blank=True, null=True)

    class Meta:
        verbose_name = _("Salary")
        verbose_name_plural = _("Salaries")
        indexes = [
            models.Index(fields=["employee", "year", "month"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(month__gte=1) & Q(month__lte=12), name="salary_month_1_12"
            ),
            models.CheckConstraint(
                check=Q(year__gte=1900), name="salary_year_gte_1900"
            ),
        ]
        ordering = ["-year", "-month", "employee_id"]

    def __str__(self) -> str:
        emp_name = getattr(self.employee, "name", str(self.employee))
        return f"{emp_name} - {self.month}/{self.year}"

    def calculate_final_salary(self) -> None:
        self.final_salary = (
            (self.base_salary or 0)
            + (self.production_bonus or 0)
            - (self.deductions or 0)
        )

    def calculate_from_evaluation(self) -> None:
        evaluations = Evaluation.objects.filter(
            employee=self.employee, month=self.month, year=self.year
        )
        total_score = evaluations.aggregate(models.Sum("score"))["score__sum"] or 0

        if total_score >= 90:
            self.production_bonus = Decimal("1000")
        elif total_score >= 70:
            self.production_bonus = Decimal("500")
        elif total_score >= 50:
            self.production_bonus = Decimal("200")
        else:
            self.production_bonus = Decimal("0")

        if total_score < 40:
            self.deductions = (self.deductions or 0) + Decimal("200")

        self.calculate_final_salary()
        self.save(update_fields=["production_bonus", "deductions", "final_salary"])

    def generate_pdf(self) -> None:
        context: dict[str, Any] = {
            "salary": self,
            "generated_at": timezone.now(),
        }
        html_string = render_to_string("payroll/salary_single_pdf.html", context)

        if not self.created_at:
            self.created_at = timezone.now()

        pdf_bytes = cast(bytes, HTML(string=html_string).write_pdf())

        salary_id: int = self.pk or 0
        file_name = (
            f"SAL-{self.created_at.strftime('%Y%m%d')}-{str(salary_id).zfill(3)}.pdf"
        )
        self.pdf_file.save(file_name, ContentFile(pdf_bytes), save=True)


class Advance(models.Model):
    class AdvanceType(models.TextChoices):
        WEEKLY = "weekly", _("أسبوعية")
        MONTHLY = "monthly", _("شهرية")

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="payroll_advances"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=AdvanceType.choices)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Advance")
        verbose_name_plural = _("Advances")
        ordering = ["-date", "-id"]
        indexes = [models.Index(fields=["employee", "date"])]

    def __str__(self) -> str:
        emp_name = getattr(self.employee, "name", str(self.employee))
        return f"{emp_name} - {self.type} - {self.amount}"


class PaymentRecord(models.Model):
    class PaymentType(models.TextChoices):
        DAILY = "daily", _("يومي")
        WEEKLY = "weekly", _("أسبوعي")
        MONTHLY = "monthly", _("شهري")

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="payroll_payment_records"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=PaymentType.choices)
    related_salary = models.ForeignKey(
        Salary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_records",
    )
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Payment record")
        verbose_name_plural = _("Payment records")
        ordering = ["-date", "-id"]
        indexes = [
            models.Index(fields=["employee", "date"]),
            models.Index(fields=["type"]),
        ]

    def __str__(self) -> str:
        emp_name = getattr(self.employee, "name", str(self.employee))
        return f"{emp_name} - {self.type} - {self.amount} - {self.date}"


class HistoricalPayment(models.Model):
    payment = models.ForeignKey(
        PaymentRecord, on_delete=models.CASCADE, related_name="historical_payments"
    )
    salary_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    date_recorded = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = _("Historical payment")
        verbose_name_plural = _("Historical payments")
        ordering = ["-date_recorded", "-id"]
        indexes = [models.Index(fields=["payment", "date_recorded"])]

    def __str__(self) -> str:
        emp_name = getattr(self.payment.employee, "name", str(self.payment.employee))
        return f"تسجيل ثابت - {emp_name} - {self.payment.date}"


class AttendanceRecord(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="payroll_attendance_records"
    )
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    is_excused_absence = models.BooleanField(default=False)
    is_absent = models.BooleanField(default=False)
    is_production_based = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Attendance record")
        verbose_name_plural = _("Attendance records")
        ordering = ["-date", "-id"]
        indexes = [models.Index(fields=["employee", "date"])]


class MonthlyIncentive(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="payroll_monthly_incentives"
    )
    month = models.DateField(help_text=_("Any date within the month being tracked"))
    commitment_bonus = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0")
    )
    quarterly_bonus = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0")
    )
    penalty_total = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0")
    )

    class Meta:
        verbose_name = _("Monthly incentive")
        verbose_name_plural = _("Monthly incentives")
        ordering = ["-month", "-id"]
        indexes = [models.Index(fields=["employee", "month"])]


class PolicySetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    value = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = _("Policy setting")
        verbose_name_plural = _("Policy settings")
        ordering = ["key"]

    def __str__(self) -> str:
        return f"{self.key}: {self.value}"
