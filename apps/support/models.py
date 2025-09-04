# ERP_CORE/internal_monitoring/models.py
from __future__ import annotations

from django.contrib.auth.models import User
from django.db import models


class InventoryDiscrepancy(models.Model):
    product = models.CharField(max_length=200, verbose_name="المنتج")
    quantity_missing = models.IntegerField(verbose_name="الكمية المفقودة")
    reported_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإبلاغ")
    resolved = models.BooleanField(default=False, verbose_name="تم الحل؟")

    def __str__(self) -> str:
        return f"عجز في المنتج {self.product} - {self.quantity_missing}"


class SuspiciousActivity(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="المستخدم"
    )
    description = models.TextField(verbose_name="وصف النشاط المشبوه")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ النشاط")
    resolved = models.BooleanField(default=False, verbose_name="تم الحل؟")

    def __str__(self) -> str:
        return f"نشاط مشبوه في {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class RiskIncident(models.Model):
    EVENT_CATEGORIES = [
        ("Stock", "مخزون"),
        ("Finance", "مالية"),
        ("Sales", "مبيعات"),
        ("System", "نظام"),
    ]
    RISK_LEVELS = [
        ("LOW", "منخفض"),
        ("MEDIUM", "متوسط"),
        ("HIGH", "مرتفع"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="المستخدم"
    )
    category = models.CharField(
        max_length=50, choices=EVENT_CATEGORIES, verbose_name="فئة الحدث"
    )
    event_type = models.CharField(max_length=100, verbose_name="نوع الحدث")
    risk_level = models.CharField(
        max_length=10, choices=RISK_LEVELS, verbose_name="مستوى المخاطر"
    )
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    # Wrapper صديق للمحلل الساكن بدل get_risk_level_display()
    def risk_level_label(self) -> str:
        mapping = dict(self.RISK_LEVELS)
        return mapping.get(self.risk_level, self.risk_level)

    def __str__(self) -> str:
        username = self.user.username if self.user else "غير معروف"
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {username} - {self.event_type} ({self.risk_level_label()})"


class ReportLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="المستخدم"
    )
    action = models.CharField(max_length=200, verbose_name="الإجراء أو البلاغ")
    details = models.TextField(blank=True, null=True, verbose_name="تفاصيل")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="التاريخ والوقت")
    is_resolved = models.BooleanField(default=False, verbose_name="تم الحل؟")
    resolution_notes = models.TextField(
        blank=True, null=True, verbose_name="ملاحظات الحل"
    )

    def __str__(self) -> str:
        username = self.user.username if self.user else "غير معروف"
        return (
            f"{username} - {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
        )


class DisciplinaryAction(models.Model):
    ACTION_TYPES = [
        ("warning", "إنذار"),
        ("suspension", "إيقاف"),
        ("deduction", "خصم"),
        ("termination", "فصل"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="المستخدم"
    )
    action_type = models.CharField(
        max_length=20, choices=ACTION_TYPES, verbose_name="نوع الإجراء"
    )
    reason = models.TextField(verbose_name="السبب")
    taken_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="actions_taken",
        verbose_name="تم بواسطة",
    )
    action_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التنفيذ")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات إضافية")

    # Wrapper صديق للمحلل الساكن بدل get_action_type_display()
    def action_type_label(self) -> str:
        mapping = dict(self.ACTION_TYPES)
        return mapping.get(self.action_type, self.action_type)

    def __str__(self) -> str:
        username = self.user.username if self.user else "غير معروف"
        return f"{username} - {self.action_type_label()} - {self.action_date.strftime('%Y-%m-%d')}"
