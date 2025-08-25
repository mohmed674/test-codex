from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

# ✅ دور القسم
class DepartmentRole(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "دور قسم"
        verbose_name_plural = "أدوار الأقسام"

# ✅ الأدوار
class Role(models.Model):
    name = models.CharField(_("Role Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    is_active = models.BooleanField(_("Is Active?"), default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="roles_created", verbose_name=_("Created By"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return self.name

class RoleRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', _("قيد الانتظار")),
        ('approved', _("تمت الموافقة")),
        ('rejected', _("مرفوض")),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    requested_role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name=_("Requested Role"))
    justification = models.TextField(_("Justification"))
    requested_at = models.DateTimeField(_("Requested At"), auto_now_add=True)

    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    response_reason = models.TextField(_("Response Reason"), blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="role_requests_reviewed", verbose_name=_("Reviewed By"))
    reviewed_at = models.DateTimeField(_("Reviewed At"), null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.requested_role.name} ({self.status})"

class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    action = models.CharField(_("Action"), max_length=100)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_("IP Address"), blank=True, null=True)
    user_agent = models.TextField(_("User Agent"), blank=True, null=True)
    location = models.CharField(_("Location"), max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"

class PermissionMatrix(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name=_("Role"))
    model_name = models.CharField(_("Model Name"), max_length=100)
    can_create = models.BooleanField(_("Can Create?"), default=False)
    can_read = models.BooleanField(_("Can Read?"), default=True)
    can_update = models.BooleanField(_("Can Update?"), default=False)
    can_delete = models.BooleanField(_("Can Delete?"), default=False)

    section = models.CharField(_("Section"), max_length=100, blank=True, null=True)
    override_reason = models.TextField(_("Override Reason"), blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="permission_matrices_created", verbose_name=_("Created By"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.role.name} - {self.model_name}"

class TemporaryAccessOverride(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name=_("Role"))
    reason = models.TextField(_("Reason"))
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="granted_overrides", verbose_name=_("Granted By"))
    granted_at = models.DateTimeField(_("Granted At"), auto_now_add=True)
    expires_at = models.DateTimeField(_("Expires At"))

    is_revoked = models.BooleanField(_("Is Revoked?"), default=False)
    revoked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="revoked_overrides", verbose_name=_("Revoked By"))
    revoked_at = models.DateTimeField(_("Revoked At"), null=True, blank=True)
    is_auto_generated = models.BooleanField(_("Auto Generated?"), default=False)
    section = models.CharField(_("Section"), max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role.name} (مؤقت)"

# ✅ المسميات الوظيفية
class JobTitle(models.Model):
    name = models.CharField(_("Job Title"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)
    salary_type = models.CharField(_("Salary Type"), max_length=20, choices=[
        ('hourly', _("Hourly")),
        ('piece', _("Piece")),
        ('fixed', _("Fixed"))
    ])
    default_piece_rate = models.DecimalField(_("Default Piece Rate"), max_digits=10, decimal_places=2, blank=True, null=True)
    hourly_rate = models.DecimalField(_("Hourly Rate"), max_digits=10, decimal_places=2, blank=True, null=True)
    default_daily_hours = models.PositiveIntegerField(_("Default Daily Hours"), default=8)

    is_active = models.BooleanField(_("Is Active?"), default=True)
    visible_on_payroll = models.BooleanField(_("Visible on Payroll?"), default=True)
    used_in_sections = ArrayField(models.CharField(max_length=100), blank=True, null=True, verbose_name=_("Used in Sections"))
    linked_to_production_stage = models.CharField(_("Linked to Production Stage"), max_length=100, blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="job_titles_created", verbose_name=_("Created By"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return self.name

# ✅ الوحدات
class Unit(models.Model):
    name = models.CharField(_("Unit Name"), max_length=50, unique=True)
    abbreviation = models.CharField(_("Abbreviation"), max_length=10)
    unit_type = models.CharField(_("Unit Type"), max_length=50, choices=[
        ("quantity", _("كمية")),
        ("weight", _("وزن")),
        ("volume", _("حجم")),
        ("time", _("وقت")),
        ("length", _("طول"))
    ], default="quantity")

    is_active = models.BooleanField(_("Is Active?"), default=True)
    is_bulk_unit = models.BooleanField(_("Is Bulk Unit?"), default=False)
    conversion_factor = models.FloatField(_("Conversion Factor"), blank=True, null=True)
    used_in_models = ArrayField(models.CharField(max_length=100), blank=True, null=True, verbose_name=_("Used in Models"))

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="units_created", verbose_name=_("Created By"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

# ✅ معايير التقييم
class EvaluationCriteria(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)
    weight = models.FloatField(_("Weight"), default=1.0)

    criteria_type = models.CharField(_("Criteria Type"), max_length=50, choices=[
        ("discipline", _("انضباط")),
        ("performance", _("أداء")),
        ("quality", _("جودة")),
        ("attendance", _("حضور")),
        ("safety", _("سلامة"))
    ], default="performance")
    applies_to_department = models.CharField(_("Applies to Department"), max_length=100, blank=True, null=True)
    is_active = models.BooleanField(_("Is Active?"), default=True)
    auto_generated = models.BooleanField(_("Auto Generated?"), default=False)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="evaluation_criteria_created", verbose_name=_("Created By"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.criteria_type}"

# ✅ مراحل الإنتاج
class ProductionStageType(models.Model):
    name = models.CharField(_("Stage Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)
    order = models.PositiveIntegerField(_("Order"))

    is_active = models.BooleanField(_("Is Active?"), default=True)
    estimated_duration_minutes = models.PositiveIntegerField(_("Estimated Duration (Minutes)"), blank=True, null=True)
    requires_machine = models.BooleanField(_("Requires Machine?"), default=False)

    linked_job_titles = models.ManyToManyField("JobTitle", blank=True, related_name="production_stages", verbose_name=_("Linked Job Titles"))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="production_stage_types_created", verbose_name=_("Created By"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.order} - {self.name}"

# ✅ حدود المخاطر
class RiskThreshold(models.Model):
    risk_type = models.CharField(_("Risk Type"), max_length=100)
    threshold_value = models.FloatField(_("Threshold Value"))
    severity_level = models.CharField(_("Severity Level"), max_length=20, choices=[
        ('low', _("منخفض")),
        ('medium', _("متوسط")),
        ('high', _("مرتفع"))
    ], default='medium')

    applies_to_section = models.CharField(_("Applies to Section"), max_length=100, blank=True, null=True)
    auto_detected_field = models.CharField(_("Auto Detected Field"), max_length=100, blank=True, null=True)
    action_required = models.TextField(_("Action Required"), blank=True, null=True)
    trigger_auto_action = models.BooleanField(_("Trigger Auto Action?"), default=False)
    is_active = models.BooleanField(_("Is Active?"), default=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="risk_thresholds_created", verbose_name=_("Created By"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.risk_type} - {self.threshold_value} ({self.severity_level})"

# ✅ الأقسام والموظفين والعملاء
class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100, unique=True)
    manager = models.CharField(max_length=200, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    job_title = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class Client(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

# ✅ نموذج الحساب الذكي
class SmartAccountTemplate(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'إيراد'),
        ('expense', 'مصروف'),
        ('asset', 'أصل'),
        ('liability', 'التزام'),
        ('equity', 'حقوق ملكية'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    suggested_debit_account = models.CharField(max_length=255)
    suggested_credit_account = models.CharField(max_length=255)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.transaction_type}"
