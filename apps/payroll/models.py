from django.db import models
from apps.employees.models import Employee
from apps.evaluation.models import Evaluation
from django.utils import timezone
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib.auth.models import User  # لموديل الحضور والمكافآت

class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_salaries')
    month = models.IntegerField()
    year = models.IntegerField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    production_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # أضفت قيمة افتراضية
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='salaries/', blank=True, null=True)  # أضفت null=True

    def __str__(self):
        return f"{self.employee.name} - {self.month}/{self.year}"

    def calculate_final_salary(self):
        self.final_salary = self.base_salary + self.production_bonus - self.deductions

    def calculate_from_evaluation(self):
        evaluations = Evaluation.objects.filter(employee=self.employee, month=self.month, year=self.year)
        total_score = evaluations.aggregate(models.Sum('score'))['score__sum'] or 0

        if total_score >= 90:
            self.production_bonus = 1000
        elif total_score >= 70:
            self.production_bonus = 500
        elif total_score >= 50:
            self.production_bonus = 200
        else:
            self.production_bonus = 0

        if total_score < 40:
            self.deductions += 200

        self.calculate_final_salary()
        self.save()

    def generate_pdf(self):
        context = {
            'salary': self,
            'generated_at': timezone.now(),
        }
        html_string = render_to_string('payroll/salary_single_pdf.html', context)
        pdf_file = HTML(string=html_string).write_pdf()
        file_name = f"SAL-{self.created_at.strftime('%Y%m%d')}-{str(self.id).zfill(3)}.pdf"
        self.pdf_file.save(file_name, ContentFile(pdf_file), save=True)


class Advance(models.Model):
    ADVANCE_TYPE_CHOICES = (
        ('weekly', 'أسبوعية'),
        ('monthly', 'شهرية'),
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_advances')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=ADVANCE_TYPE_CHOICES)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee.name} - {self.type} - {self.amount}"


class PaymentRecord(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري'),
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_payment_records')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    related_salary = models.ForeignKey(Salary, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_records')
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.type} - {self.amount} - {self.date}"


class HistoricalPayment(models.Model):
    payment = models.ForeignKey(PaymentRecord, on_delete=models.CASCADE, related_name='historical_payments')
    salary_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    date_recorded = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"تسجيل ثابت - {self.payment.employee.name} - {self.payment.date}"


class AttendanceRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_attendance_records')  # إضافة related_name
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    is_excused_absence = models.BooleanField(default=False)
    is_absent = models.BooleanField(default=False)
    is_production_based = models.BooleanField(default=False)


class MonthlyIncentive(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_monthly_incentives')  # إضافة related_name
    month = models.DateField()
    commitment_bonus = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    quarterly_bonus = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    penalty_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)


class PolicySetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    value = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.key}: {self.value}"
