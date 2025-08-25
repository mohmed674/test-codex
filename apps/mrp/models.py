# mrp/models.py
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from apps.products.models import Product
from apps.production.models import BillOfMaterials
from apps.purchases.models import PurchaseRequest


DEC_ZERO = Decimal("0.000")


class PlanningType(models.TextChoices):
    MRP = "MRP", _("تخطيط احتياجات المواد")
    MPS = "MPS", _("جدولة الإنتاج الرئيسي")
    MANUAL = "MANUAL", _("يدوي")


class PlanningStatus(models.TextChoices):
    DRAFT = "DRAFT", _("مسودة")
    CONFIRMED = "CONFIRMED", _("مؤكد")
    RUNNING = "RUNNING", _("قيد التشغيل")
    COMPLETED = "COMPLETED", _("مكتمل")
    CANCELLED = "CANCELLED", _("ملغى")
    LOCKED = "LOCKED", _("مغلق")


class DemandSource(models.TextChoices):
    MANUAL = "MANUAL", _("مدخل يدويًا")
    SALES_ORDER = "SO", _("أمر بيع")
    FORECAST = "FC", _("تنبؤ")
    PROJECT = "PRJ", _("مشروع")


class Severity(models.TextChoices):
    LOW = "LOW", _("منخفض")
    MEDIUM = "MEDIUM", _("متوسط")
    HIGH = "HIGH", _("مرتفع")
    CRITICAL = "CRIT", _("حرج")


class SuggestionType(models.TextChoices):
    BUY = "BUY", _("شراء")
    MAKE = "MAKE", _("تصنيع")
    TRANSFER = "TRANSFER", _("تحويل مخزني")


class SuggestionStatus(models.TextChoices):
    DRAFT = "DRAFT", _("مسودة")
    APPROVED = "APPROVED", _("معتمد")
    REJECTED = "REJECTED", _("مرفوض")
    EXECUTED = "EXECUTED", _("تم التنفيذ")
    CANCELLED = "CANCELLED", _("ملغى")


class MaterialPlanning(models.Model):
    code = models.CharField(_("كود التخطيط"), max_length=40, unique=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="material_plans", verbose_name=_("المنتج"))
    planned_quantity = models.DecimalField(
        _("الكمية المخطط لها"),
        max_digits=16,
        decimal_places=3,
        validators=[MinValueValidator(DEC_ZERO)],
    )
    uom_code = models.CharField(_("وحدة القياس (رمز)"), max_length=16, blank=True, default="")
    required_date = models.DateField(_("تاريخ الحاجة"))
    warehouse = models.CharField(_("المخزن/الموقع"), max_length=64, blank=True, default="")
    planning_type = models.CharField(_("نوع التخطيط"), max_length=10, choices=PlanningType.choices, default=PlanningType.MRP)
    status = models.CharField(_("الحالة"), max_length=12, choices=PlanningStatus.choices, default=PlanningStatus.DRAFT, db_index=True)
    priority = models.PositiveSmallIntegerField(_("الأولوية"), default=2)  # 1 عاجلة – 2 عادية – 3 منخفضة
    version = models.PositiveIntegerField(_("الإصدار"), default=1)
    demand_source = models.CharField(_("مصدر الطلب"), max_length=8, choices=DemandSource.choices, default=DemandSource.MANUAL)
    demand_ref = models.CharField(_("مرجع المصدر"), max_length=64, blank=True, default="")
    auto_generated = models.BooleanField(_("مولّد تلقائيًا"), default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("أُنشئ بواسطة")
    )
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)

    class Meta:
        verbose_name = _("تخطيط مواد")
        verbose_name_plural = _("تخطيطات المواد")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "required_date")),
            models.Index(fields=("product", "required_date")),
        ]

    def __str__(self):
        return f"{self.code or 'PLAN'} — {self.product} × {self.planned_quantity} @ {self.required_date}"

    @property
    def total_required(self):
        return (self.lines.aggregate(s=models.Sum("required_qty"))["s"] or DEC_ZERO)

    @property
    def total_available(self):
        return (self.lines.aggregate(s=models.Sum("available_qty"))["s"] or DEC_ZERO)

    @property
    def total_reserved(self):
        return (self.lines.aggregate(s=models.Sum("reserved_qty"))["s"] or DEC_ZERO)

    @property
    def total_shortage(self):
        return (self.lines.aggregate(s=models.Sum("shortage_qty"))["s"] or DEC_ZERO)


class MaterialLine(models.Model):
    planning = models.ForeignKey(MaterialPlanning, on_delete=models.CASCADE, related_name="lines", verbose_name=_("تخطيط"))
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("شجرة مكونات"))
    material = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="mrp_lines", verbose_name=_("مادة/خامة"))
    uom_code = models.CharField(_("وحدة القياس (رمز)"), max_length=16, blank=True, default="")
    required_qty = models.DecimalField(
        _("كمية مطلوبة"),
        max_digits=16,
        decimal_places=3,
        validators=[MinValueValidator(DEC_ZERO)],
    )
    available_qty = models.DecimalField(
        _("متاح"),
        max_digits=16,
        decimal_places=3,
        default=DEC_ZERO,
        validators=[MinValueValidator(DEC_ZERO)],
    )
    reserved_qty = models.DecimalField(
        _("محجوز"),
        max_digits=16,
        decimal_places=3,
        default=DEC_ZERO,
        validators=[MinValueValidator(DEC_ZERO)],
    )
    shortage_qty = models.DecimalField(
        _("عجز"),
        max_digits=16,
        decimal_places=3,
        default=DEC_ZERO,
        validators=[MinValueValidator(DEC_ZERO)],
        help_text=_("يُحسب = المطلوب − (المتاح − المحجوز) ولا يقل عن صفر."),
    )
    source_location = models.CharField(_("الموقع/المصدر"), max_length=64, blank=True, default="")
    notes = models.TextField(_("ملاحظات"), blank=True, default="")
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)

    class Meta:
        verbose_name = _("سطر تخطيط مادة")
        verbose_name_plural = _("سطور تخطيط المواد")
        ordering = ("material__name",)
        constraints = [
            models.UniqueConstraint(fields=("planning", "material"), name="uq_mrp_line_planning_material"),
        ]
        indexes = [
            models.Index(fields=("material",)),
        ]

    def __str__(self):
        return f"{self.material} — req:{self.required_qty} avail:{self.available_qty} res:{self.reserved_qty} sh:{self.shortage_qty}"

    def save(self, *args, **kwargs):
        # احسب العجز: المطلوب − (المتاح − المحجوز) ولا يقل عن صفر
        needed = (self.required_qty or DEC_ZERO)
        stock_free = (self.available_qty or DEC_ZERO) - (self.reserved_qty or DEC_ZERO)
        shortage = needed - stock_free
        if shortage < DEC_ZERO:
            shortage = DEC_ZERO
        self.shortage_qty = shortage
        super().save(*args, **kwargs)


class ProcurementSuggestion(models.Model):
    line = models.OneToOneField(MaterialLine, on_delete=models.CASCADE, related_name="suggestion", verbose_name=_("سطر التخطيط"))
    suggestion_type = models.CharField(_("نوع الاقتراح"), max_length=10, choices=SuggestionType.choices, db_index=True)
    suggested_qty = models.DecimalField(
        _("الكمية المقترحة"),
        max_digits=16, decimal_places=3, validators=[MinValueValidator(DEC_ZERO)]
    )
    due_date = models.DateField(_("تاريخ الاستحقاق"))
    target_warehouse = models.CharField(_("المخزن الهدف"), max_length=64, blank=True, default="")
    vendor_hint = models.CharField(_("مورد مُقترح (اختياري)"), max_length=128, blank=True, default="")
    purchase_request = models.ForeignKey(
        PurchaseRequest, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("طلب شراء")
    )
    status = models.CharField(_("حالة الاقتراح"), max_length=12, choices=SuggestionStatus.choices, default=SuggestionStatus.DRAFT)
    auto_generated = models.BooleanField(_("مولَّد تلقائيًا"), default=True)
    notes = models.TextField(_("ملاحظات"), blank=True, default="")
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)

    class Meta:
        verbose_name = _("اقتراح توريد/تصنيع")
        verbose_name_plural = _("اقتراحات التوريد/التصنيع")
        ordering = ("status", "due_date")
        indexes = [
            models.Index(fields=("status", "due_date")),
        ]

    def __str__(self):
        return f"{self.get_suggestion_type_display()} — {self.suggested_qty} ({self.status})"


class PlanningException(models.Model):
    planning = models.ForeignKey(MaterialPlanning, on_delete=models.CASCADE, related_name="exceptions", verbose_name=_("تخطيط"))
    line = models.ForeignKey(MaterialLine, on_delete=models.SET_NULL, null=True, blank=True, related_name="exceptions", verbose_name=_("سطر"))
    code = models.CharField(_("الكود"), max_length=32)
    message = models.CharField(_("الرسالة"), max_length=255)
    severity = models.CharField(_("الخطورة"), max_length=6, choices=Severity.choices, default=Severity.MEDIUM)
    resolved = models.BooleanField(_("محلول؟"), default=False)
    resolved_at = models.DateTimeField(_("تاريخ الحل"), null=True, blank=True)
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)

    class Meta:
        verbose_name = _("استثناء تخطيط")
        verbose_name_plural = _("استثناءات التخطيط")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.code} [{self.severity}] — {self.message[:40]}"
