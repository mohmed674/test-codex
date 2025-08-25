from django.db import models
from apps.employees.models import Employee
from datetime import date
from django.utils.translation import gettext_lazy as _

class DisciplineRecord(models.Model):
    class TypeChoices(models.TextChoices):
        DEDUCTION = 'خصم', _('خصم')
        BONUS = 'مكافأة', _('مكافأة')
        WARNING = 'إنذار', _('إنذار')

    class ValueTypeChoices(models.TextChoices):
        AMOUNT = 'مبلغ', _('مبلغ')
        PERCENT = 'نسبة', _('نسبة')

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="الموظف")
    date = models.DateField(auto_now_add=True, verbose_name="تاريخ الإجراء")
    type = models.CharField(max_length=50, choices=TypeChoices.choices, verbose_name="نوع الإجراء")
    value_type = models.CharField(max_length=10, choices=ValueTypeChoices.choices, default=ValueTypeChoices.AMOUNT, verbose_name="نوع القيمة")
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="القيمة")
    reason = models.TextField(verbose_name="السبب")
    created_by = models.CharField(max_length=100, verbose_name="تم بواسطة")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    related_month = models.CharField(max_length=7, blank=True, null=True, verbose_name="الشهر المرتبط")
    is_approved = models.BooleanField(default=True, verbose_name="معتمد؟")

    def save(self, *args, **kwargs):
        # ✅ توليد الشهر تلقائيًا إذا لم يتم تحديده
        if not self.related_month and self.date:
            self.related_month = self.date.strftime('%Y-%m')

        # ✅ تطبيق منطق ذكي: الإنذارات ليس لها قيمة مالية
        if self.type == self.TypeChoices.WARNING:
            self.value = None
            self.value_type = self.ValueTypeChoices.AMOUNT

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.type} - {self.date}"

    class Meta:
        verbose_name = "سجل إجراء تأديبي"
        verbose_name_plural = "السجلات التأديبية"
        ordering = ['-date']
