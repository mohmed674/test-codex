from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    # Forward references for type checkers without importing at runtime.
    pass

logger = logging.getLogger(__name__)


# ✅ دور القسم
class DepartmentRole(models.Model):
    """
    Represents a generic role within a department context.
    """

    name = models.CharField(max_length=100, unique=True, verbose_name=_("اسم الدور"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط؟"))

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("دور قسم")
        verbose_name_plural = _("أدوار الأقسام")


# ✅ الأدوار
class Role(models.Model):
    """
    System-wide role entity to group permissions and access rules.
    """

    name = models.CharField(_("Role Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    is_active = models.BooleanField(_("Is Active?"), default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roles_created",
        verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("دور")
        verbose_name_plural = _("أدوار")


class RoleRequest(models.Model):
    """
    A user's request to obtain a specific role, with approval workflow.
    """

    STATUS_CHOICES = [
        ("pending", _("قيد الانتظار")),
        ("approved", _("تمت الموافقة")),
        ("rejected", _("مرفوض")),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    requested_role = models.ForeignKey(
        Role, on_delete=models.CASCADE, verbose_name=_("Requested Role")
    )
    justification = models.TextField(_("Justification"))
    requested_at = models.DateTimeField(_("Requested At"), auto_now_add=True)

    status = models.CharField(
        _("Status"), max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    response_reason = models.TextField(_("Response Reason"), blank=True, null=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_requests_reviewed",
        verbose_name=_("Reviewed By"),
    )
    reviewed_at = models.DateTimeField(_("Reviewed At"), null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.requested_role.name} ({self.status})"

    class Meta:
        verbose_name = _("طلب دور")
        verbose_name_plural = _("طلبات الأدوار")


class AccessLog(models.Model):
    """
    Audit log for user actions and access events.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    action = models.CharField(_("Action"), max_length=100)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_("IP Address"), blank=True, null=True)
    user_agent = models.TextField(_("User Agent"), blank=True, null=True)
    location = models.CharField(_("Location"), max_length=100, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.action} at {self.timestamp}"

    class Meta:
        verbose_name = _("سجل وصول")
        verbose_name_plural = _("سجلات الوصول")


class PermissionMatrix(models.Model):
    """
    Permission matrix per role and model with CRUD granularity.
    """

    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name=_("Role"))
    model_name = models.CharField(_("Model Name"), max_length=100)
    can_create = models.BooleanField(_("Can Create?"), default=False)
    can_read = models.BooleanField(_("Can Read?"), default=True)
    can_update = models.BooleanField(_("Can Update?"), default=False)
    can_delete = models.BooleanField(_("Can Delete?"), default=False)

    section = models.CharField(_("Section"), max_length=100, blank=True, null=True)
    override_reason = models.TextField(_("Override Reason"), blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="permission_matrices_created",
        verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.role.name} - {self.model_name}"

    class Meta:
        verbose_name = _("مصفوفة صلاحيات")
        verbose_name_plural = _("مصفوفات الصلاحيات")


class TemporaryAccessOverride(models.Model):
    """
    Temporary override that grants a user a role for a limited time.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name=_("Role"))
    reason = models.TextField(_("Reason"))
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_overrides",
        verbose_name=_("Granted By"),
    )
    granted_at = models.DateTimeField(_("Granted At"), auto_now_add=True)
    expires_at = models.DateTimeField(_("Expires At"))

    is_revoked = models.BooleanField(_("Is Revoked?"), default=False)
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revoked_overrides",
        verbose_name=_("Revoked By"),
    )
    revoked_at = models.DateTimeField(_("Revoked At"), null=True, blank=True)
    is_auto_generated = models.BooleanField(_("Auto Generated?"), default=False)
    section = models.CharField(_("Section"), max_length=100, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.role.name} ({_('مؤقت')})"

    class Meta:
        verbose_name = _("تجاوز وصول مؤقت")
        verbose_name_plural = _("تجاوزات الوصول المؤقتة")


# ✅ المسميات الوظيفية
class JobTitle(models.Model):
    """
    Job title with compensation metadata and visibility flags.
    """

    name = models.CharField(_("Job Title"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)
    salary_type = models.CharField(
        _("Salary Type"),
        max_length=20,
        choices=[("hourly", _("Hourly")), ("piece", _("Piece")), ("fixed", _("Fixed"))],
    )
    default_piece_rate = models.DecimalField(
        _("Default Piece Rate"), max_digits=10, decimal_places=2, blank=True, null=True
    )
    hourly_rate = models.DecimalField(
        _("Hourly Rate"), max_digits=10, decimal_places=2, blank=True, null=True
    )
    default_daily_hours = models.PositiveIntegerField(
        _("Default Daily Hours"), default=8
    )

    is_active = models.BooleanField(_("Is Active?"), default=True)
    visible_on_payroll = models.BooleanField(_("Visible on Payroll?"), default=True)
    used_in_sections = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        null=True,
        verbose_name=_("Used in Sections"),
    )
    linked_to_production_stage = models.CharField(
        _("Linked to Production Stage"), max_length=100, blank=True, null=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="job_titles_created",
        verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("مسمى وظيفي")
        verbose_name_plural = _("مسميات وظيفية")


# ✅ الوحدات
class Unit(models.Model):
    """
    Measurement unit with conversion and usage metadata.
    """

    name = models.CharField(_("Unit Name"), max_length=50, unique=True)
    abbreviation = models.CharField(_("Abbreviation"), max_length=10)
    unit_type = models.CharField(
        _("Unit Type"),
        max_length=50,
        choices=[
            ("quantity", _("كمية")),
            ("weight", _("وزن")),
            ("volume", _("حجم")),
            ("time", _("وقت")),
            ("length", _("طول")),
        ],
        default="quantity",
    )

    is_active = models.BooleanField(_("Is Active?"), default=True)
    is_bulk_unit = models.BooleanField(_("Is Bulk Unit?"), default=False)
    conversion_factor = models.FloatField(_("Conversion Factor"), blank=True, null=True)
    used_in_models = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        null=True,
        verbose_name=_("Used in Models"),
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="units_created",
        verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.abbreviation})"

    class Meta:
        verbose_name = _("وحدة")
        verbose_name_plural = _("وحدات")


# ✅ معايير التقييم
class EvaluationCriteria(models.Model):
    """
    Weighted evaluation criteria applicable to departments or employees.
    """

    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)
    weight = models.FloatField(_("Weight"), default=1.0)

    criteria_type = models.CharField(
        _("Criteria Type"),
        max_length=50,
        choices=[
            ("discipline", _("انضباط")),
            ("performance", _("أداء")),
            ("quality", _("جودة")),
            ("attendance", _("حضور")),
            ("safety", _("سلامة")),
        ],
        default="performance",
    )
    applies_to_department = models.CharField(
        _("Applies to Department"), max_length=100, blank=True, null=True
    )
    is_active = models.BooleanField(_("Is Active?"), default=True)
    auto_generated = models.BooleanField(_("Auto Generated?"), default=False)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evaluation_criteria_created",
        verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.criteria_type}"

    class Meta:
        verbose_name = _("معيار تقييم")
        verbose_name_plural = _("معايير التقييم")


# ✅ مراحل الإنتاج
class ProductionStageType(models.Model):
    """
    Production pipeline stage definition and required capabilities.
    """

    name = models.CharField(_("Stage Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)
    order = models.PositiveIntegerField(_("Order"))

    is_active = models.BooleanField(_("Is Active?"), default=True)
    estimated_duration_minutes = models.PositiveIntegerField(
        _("Estimated Duration (Minutes)"), blank=True, null=True
    )
    requires_machine = models.BooleanField(_("Requires Machine?"), default=False)

    # Keep the annotation non-parameterized to avoid IDE/mypy name resolution issues.
    linked_job_titles: models.ManyToManyField = models.ManyToManyField(
        "JobTitle",
        blank=True,
        related_name="production_stages",
        verbose_name=_("Linked Job Titles"),
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="production_stage_types_created",
        verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.order} - {self.name}"

    class Meta:
        verbose_name = _("مرحلة إنتاج")
        verbose_name_plural = _("مراحل الإنتاج")


# ✅ حدود المخاطر
class RiskThreshold(models.Model):
    """
    Threshold configuration for risk detection with severity classification.
    """

    risk_type = models.CharField(_("Risk Type"), max_length=100)
    threshold_value = models.FloatField(_("Threshold Value"))
    severity_level = models.CharField(
        _("Severity Level"),
        max_length=20,
        choices=[("low", _("منخفض")), ("medium", _("متوسط")), ("high", _("مرتفع"))],
        default="medium",
    )

    applies_to_section = models.CharField(
        _("Applies to Section"), max_length=100, blank=True, null=True
    )
    auto_detected_field = models.CharField(
        _("Auto Detected Field"), max_length=100, blank=True, null=True
    )
    action_required = models.TextField(_("Action Required"), blank=True, null=True)
    trigger_auto_action = models.BooleanField(_("Trigger Auto Action?"), default=False)
    is_active = models.BooleanField(_("Is Active?"), default=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="risk_thresholds_created",
        verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.risk_type} - {self.threshold_value} ({self.severity_level})"

    class Meta:
        verbose_name = _("حد مخاطر")
        verbose_name_plural = _("حدود المخاطر")


# ✅ الأقسام والموظفين والعملاء
class Department(models.Model):
    """
    Organizational department with optional manager and notes.
    """

    name = models.CharField(max_length=200, verbose_name=_("الاسم"))
    code = models.CharField(max_length=100, unique=True, verbose_name=_("الرمز"))
    manager = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=_("المدير")
    )
    note = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("قسم")
        verbose_name_plural = _("أقسام")


class Employee(models.Model):
    """
    Employee profile linked to Django auth user.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("User"))
    name = models.CharField(max_length=200, verbose_name=_("الاسم"))
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("القسم"),
    )
    job_title = models.CharField(max_length=200, verbose_name=_("المسمى الوظيفي"))
    email = models.EmailField(
        blank=True, null=True, verbose_name=_("البريد الإلكتروني")
    )
    phone = models.CharField(
        max_length=50, blank=True, null=True, verbose_name=_("الهاتف")
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("موظف")
        verbose_name_plural = _("موظفون")


class Client(models.Model):
    """
    Customer record with basic contact information and loyalty points.
    """

    name = models.CharField(max_length=200, verbose_name=_("الاسم"))
    email = models.EmailField(
        blank=True, null=True, verbose_name=_("البريد الإلكتروني")
    )
    phone = models.CharField(
        max_length=50, blank=True, null=True, verbose_name=_("الهاتف")
    )
    address = models.TextField(blank=True, null=True, verbose_name=_("العنوان"))
    points = models.PositiveIntegerField(default=0, verbose_name=_("النقاط"))

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("عميل")
        verbose_name_plural = _("عملاء")


# ✅ نموذج الحساب الذكي
class SmartAccountTemplate(models.Model):
    """
    Smart accounting template providing suggested debit/credit mappings per transaction type.
    """

    TRANSACTION_TYPES = [
        ("income", _("إيراد")),
        ("expense", _("مصروف")),
        ("asset", _("أصل")),
        ("liability", _("التزام")),
        ("equity", _("حقوق ملكية")),
    ]

    name = models.CharField(max_length=255, verbose_name=_("الاسم"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES, verbose_name=_("نوع المعاملة")
    )
    suggested_debit_account = models.CharField(
        max_length=255, verbose_name=_("الحساب المدين المقترح")
    )
    suggested_credit_account = models.CharField(
        max_length=255, verbose_name=_("الحساب الدائن المقترح")
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("أُنشئ بواسطة"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("أُنشئ في"))

    is_active = models.BooleanField(default=True, verbose_name=_("نشط؟"))

    def __str__(self) -> str:
        return f"{self.name} - {self.transaction_type}"

    class Meta:
        verbose_name = _("قالب حساب ذكي")
        verbose_name_plural = _("قوالب الحساب الذكي")
