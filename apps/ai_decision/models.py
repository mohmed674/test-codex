from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.employees.models import Employee


class AlertLevel(models.TextChoices):
    INFO = "info", _("معلومة")
    WARNING = "warning", _("تحذير")
    SUCCESS = "success", _("نجاح")
    DANGER = "danger", _("خطر")


class AlertSection(models.TextChoices):
    SALES = "sales", _("المبيعات")
    PRODUCTION = "production", _("الإنتاج")
    SYSTEM = "system", _("النظام")
    OTHER = "other", _("أخرى")


class AIDecisionAlert(models.Model):
    """
    تنبيه/إنذار يخلقه النظام الذكي لقرار معيّن.
    حُدِّث ليتوافق مع الاستخدام في العروض والإشارات والمهام.
    """

    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("العنوان"),
    )
    message = models.TextField(
        blank=True,
        default="",
        verbose_name=_("نص التنبيه"),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("وصف إضافي"),
    )

    section = models.CharField(
        max_length=32,
        choices=AlertSection.choices,
        default=AlertSection.OTHER,
        db_index=True,
        verbose_name=_("القسم"),
    )
    alert_type = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        verbose_name=_("نوع التنبيه"),
    )
    level = models.CharField(
        max_length=16,
        choices=AlertLevel.choices,
        default=AlertLevel.INFO,
        db_index=True,
        verbose_name=_("المستوى"),
    )

    is_resolved = models.BooleanField(
        default=False,
        verbose_name=_("تمت المعالجة"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
        db_index=True,
    )

    class Meta:
        verbose_name = _("تنبيه قرار")
        verbose_name_plural = _("تنبيهات القرارات")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("section", "created_at")),
            models.Index(fields=("level", "created_at")),
            models.Index(fields=("is_resolved",)),
        ]

    def __str__(self) -> str:
        base = self.title or (self.alert_type or _("تنبيه"))
        return f"{base} [{self.section}/{self.level}]"


class DecisionAnalysis(models.Model):
    """
    سجل تحليل قرار (يدوي/آلي) مرتبط بموظف.
    حُدِّث لإضافة description/accuracy لتتوافق مع التحليلات.
    """

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="decisions",
        verbose_name=_("الموظف"),
    )
    decision_type = models.CharField(
        max_length=100,
        verbose_name=_("نوع القرار"),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("الوصف"),
    )
    accuracy = models.FloatField(
        default=0.0,
        verbose_name=_("دقّة التحليل"),
    )

    production_score = models.FloatField(verbose_name=_("تقييم الإنتاج"))
    behavior_score = models.FloatField(verbose_name=_("تقييم السلوك"))
    financial_impact = models.FloatField(verbose_name=_("الأثر المالي"))
    final_suggestion = models.CharField(
        max_length=255,
        verbose_name=_("التوصية النهائية"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
        db_index=True,
    )

    class Meta:
        verbose_name = _("تحليل قرار")
        verbose_name_plural = _("تحليلات القرارات")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("employee", "created_at")),
            models.Index(fields=("decision_type",)),
        ]

    def __str__(self) -> str:
        return f"{self.employee} - {self.decision_type}"


class AIDecisionLog(models.Model):
    """
    سجل أحداث/وقائع مرتبطة بقرارات الذكاء.
    يستخدمه signals لتسجيل المخاطر والحالات.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المستخدم"),
    )
    event_type = models.CharField(
        max_length=100,
        verbose_name=_("نوع الحدث"),
        db_index=True,
    )
    description = models.TextField(verbose_name=_("الوصف"))
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ("Low", _("منخفض")),
            ("Medium", _("متوسط")),
            ("High", _("مرتفع")),
        ],
        default="Medium",
        verbose_name=_("درجة الخطورة"),
        db_index=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء"),
        db_index=True,
    )

    class Meta:
        verbose_name = _("سجل قرار ذكاء")
        verbose_name_plural = _("سجلات قرارات الذكاء")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("event_type", "created_at")),
            models.Index(fields=("risk_level", "created_at")),
        ]

    def __str__(self) -> str:
        user = str(self.user) if self.user else _("مجهول")
        return f"{user} - {self.event_type} ({self.risk_level})"
