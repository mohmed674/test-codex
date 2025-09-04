# apps/internal_monitoring/models.py
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class DisciplinaryAction(models.Model):
    """إجراءات تأديبية مرتبطة بمستخدم."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="disciplinary_actions",
        verbose_name="المستخدم",
    )
    taken_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actions_taken_internal_monitoring",
        verbose_name="تم بواسطة",
    )
    reason = models.TextField(verbose_name="السبب")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "إجراء تأديبي"
        verbose_name_plural = "إجراءات تأديبية"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user} - {self.reason[:30]}"


class ReportLog(models.Model):
    """سجل تقارير مرتبطة بمستخدم."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="internal_report_logs",
        verbose_name="المستخدم",
    )
    message = models.CharField(max_length=255, verbose_name="الرسالة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "سجل تقرير"
        verbose_name_plural = "سجلات تقارير"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user} - {self.message}"


class RiskIncident(models.Model):
    """حوادث مرتبطة بالمخاطر."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="risk_incidents",
        verbose_name="المستخدم",
    )
    description = models.TextField(verbose_name="الوصف")
    severity = models.CharField(
        max_length=20,
        choices=[("low", "منخفض"), ("medium", "متوسط"), ("high", "مرتفع")],
        default="low",
        verbose_name="الخطورة",
    )
    reported_at = models.DateTimeField(default=timezone.now, verbose_name="تاريخ التبليغ")

    class Meta:
        verbose_name = "حادث مخاطر"
        verbose_name_plural = "حوادث مخاطر"
        ordering = ["-reported_at"]

    def __str__(self) -> str:
        return f"{self.severity.upper()} - {self.description[:30]}"


class SuspiciousActivity(models.Model):
    """نشاط مشبوه مرتبط بمستخدم."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="suspicious_activities",
        verbose_name="المستخدم",
    )
    activity_type = models.CharField(max_length=100, verbose_name="نوع النشاط")
    details = models.TextField(blank=True, null=True, verbose_name="تفاصيل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "نشاط مشبوه"
        verbose_name_plural = "أنشطة مشبوهة"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user} - {self.activity_type}"


class InventoryDiscrepancy(models.Model):
    """الفروقات في المخزون."""

    product_name = models.CharField(max_length=255, verbose_name="اسم المنتج")
    expected_qty = models.IntegerField(verbose_name="الكمية المتوقعة")
    actual_qty = models.IntegerField(verbose_name="الكمية الفعلية")
    detected_at = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الاكتشاف")

    class Meta:
        verbose_name = "فرق جرد"
        verbose_name_plural = "فروق جرد"
        ordering = ["-detected_at"]

    def __str__(self) -> str:
        return f"{self.product_name}: {self.expected_qty} vs {self.actual_qty}"
