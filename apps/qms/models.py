# -*- coding: utf-8 -*-
# QMS — Quality Management System (AQL / SPC / CAPA)
# Django models aligned with Odoo/SAP best practices (through 2025)
#
# Notes:
# - Keep all FKs nullable/optional to avoid hard coupling. Use Generic relations where helpful.
# - Seed tables for AQL (code letters & sampling plans) should be loaded via fixtures/migrations.
# - KPIs, dashboards, and workflows can be layered on top without changing data model.

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# -----------------------------
# Common / Base
# -----------------------------

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("أُنشئ بواسطة"),
        null=True, blank=True, on_delete=models.SET_NULL, related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("عُدّل بواسطة"),
        null=True, blank=True, on_delete=models.SET_NULL, related_name="%(class)s_updated"
    )
    notes = models.TextField(_("ملاحظات"), null=True, blank=True)

    class Meta:
        abstract = True


# -----------------------------
# Master Data: Characteristics & Defects
# -----------------------------

class MeasurementType(models.TextChoices):
    VARIABLE = "variable", _("قياسي/متغير (Numeric)")
    ATTRIBUTE = "attribute", _("وصفـي/سِمـي (Attribute)")


class SeverityClass(models.TextChoices):
    CRITICAL = "critical", _("حرِج")
    MAJOR    = "major", _("كبير")
    MINOR    = "minor", _("ثانوي")


class QualityCharacteristic(TimeStampedModel):
    """
    A measurable or attribute characteristic (CTQ/CTP) attached to a product/item/process.
    """
    key = models.CharField(_("المفتاح/الكود"), max_length=64, unique=True)
    name = models.CharField(_("اسم الخاصية"), max_length=255)
    measurement_type = models.CharField(_("نوع القياس"), max_length=16, choices=MeasurementType.choices, default=MeasurementType.VARIABLE)

    # Optional references (loose coupling)
    product = models.ForeignKey("products.Product", verbose_name=_("المنتج"), null=True, blank=True, on_delete=models.SET_NULL)
    inventory_item = models.ForeignKey("inventory.InventoryItem", verbose_name=_("عنصر مخزون"), null=True, blank=True, on_delete=models.SET_NULL)

    unit = models.CharField(_("وحدة القياس"), max_length=32, null=True, blank=True)
    target = models.DecimalField(_("القيمة المستهدفة"), max_digits=14, decimal_places=6, null=True, blank=True)
    lsl = models.DecimalField(_("الحد الأدنى المسموح (LSL)"), max_digits=14, decimal_places=6, null=True, blank=True)
    usl = models.DecimalField(_("الحد الأقصى المسموح (USL)"), max_digits=14, decimal_places=6, null=True, blank=True)
    decimal_places = models.PositiveSmallIntegerField(_("عدد المنازل العشرية"), default=2)

    is_active = models.BooleanField(_("نشِطة؟"), default=True)

    class Meta:
        verbose_name = _("خاصية جودة")
        verbose_name_plural = _("خصائص الجودة")
        indexes = [
            models.Index(fields=["key"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.key} — {self.name}"


class DefectType(TimeStampedModel):
    """
    Standardized defect taxonomy to be used in AQL inspections (Critical/Major/Minor).
    """
    code = models.CharField(_("الكود"), max_length=32, unique=True)
    name = models.CharField(_("اسم العيب"), max_length=255)
    severity = models.CharField(_("الخطورة"), max_length=16, choices=SeverityClass.choices, default=SeverityClass.MAJOR)
    description = models.TextField(_("الوصف"), null=True, blank=True)
    is_active = models.BooleanField(_("نشِط؟"), default=True)

    class Meta:
        verbose_name = _("نوع عيب")
        verbose_name_plural = _("أنواع العيوب")
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["severity"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name} ({self.get_severity_display()})"


# -----------------------------
# AQL / Sampling (ISO 2859-1 / MIL-STD-105E aligned)
# -----------------------------

class InspectionStage(models.TextChoices):
    INCOMING = "incoming", _("فحص وارد")
    IN_PROCESS = "in_process", _("فحص أثناء العملية")
    FINAL = "final", _("فحص نهائي")


class InspectionLevel(models.TextChoices):
    S1 = "S1", "S1"
    S2 = "S2", "S2"
    S3 = "S3", "S3"
    S4 = "S4", "S4"
    GI = "GI", "GI"
    GII = "GII", "GII"
    GIII = "GIII", "GIII"


class SamplingMode(models.TextChoices):
    NORMAL = "normal", _("عادي")
    TIGHTENED = "tightened", _("مشدد")
    REDUCED = "reduced", _("مخفض")


class AQLPlan(TimeStampedModel):
    """
    Defines an AQL plan (e.g., ISO 2859-1) with level & mode.
    Sampling rows are in AQLSamplingRow; code letters mapping in AQLCodeLetter.
    """
    name = models.CharField(_("الاسم"), max_length=128, unique=True)
    standard = models.CharField(_("المعيار"), max_length=64, default="ISO 2859-1 / MIL-STD-105E")
    stage = models.CharField(_("مرحلة الفحص"), max_length=16, choices=InspectionStage.choices, default=InspectionStage.INCOMING)
    level = models.CharField(_("مستوى الفحص"), max_length=4, choices=InspectionLevel.choices, default=InspectionLevel.GII)
    aql = models.DecimalField(_("قيمة AQL"), max_digits=5, decimal_places=2, help_text=_("مثال: 0.65 ، 1.0 ، 2.5"), db_index=True)
    mode = models.CharField(_("نمط السحب"), max_length=12, choices=SamplingMode.choices, default=SamplingMode.NORMAL)
    effective_from = models.DateField(_("ساري من"), default=timezone.now)
    is_active = models.BooleanField(_("نشط؟"), default=True)

    class Meta:
        verbose_name = _("خطة AQL")
        verbose_name_plural = _("خطط AQL")
        indexes = [
            models.Index(fields=["aql", "level", "mode", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} (AQL {self.aql} {self.level}/{self.mode})"


class AQLCodeLetter(TimeStampedModel):
    """
    Code letter mapping by lot size for a given plan & level (e.g., Lot 281-500 -> Code 'J').
    """
    plan = models.ForeignKey(AQLPlan, on_delete=models.CASCADE, related_name="code_letters", verbose_name=_("الخطة"))
    lot_size_from = models.PositiveIntegerField(_("حجم الدفعة من"), db_index=True)
    lot_size_to = models.PositiveIntegerField(_("حجم الدفعة إلى"), db_index=True)
    code_letter = models.CharField(_("رمز الحرف"), max_length=2, db_index=True)

    class Meta:
        verbose_name = _("حرف الكود حسب حجم الدفعة")
        verbose_name_plural = _("أحرف الأكواد حسب حجم الدفعة")
        constraints = [
            models.UniqueConstraint(fields=["plan", "lot_size_from", "lot_size_to", "code_letter"], name="uq_aql_codeletter_range"),
        ]
        indexes = [
            models.Index(fields=["plan", "code_letter"]),
        ]

    def __str__(self) -> str:
        return f"{self.plan} — {self.lot_size_from}-{self.lot_size_to} => {self.code_letter}"


class AQLSamplingRow(TimeStampedModel):
    """
    Sampling size & acceptance numbers for a given plan and code letter.
    """
    plan = models.ForeignKey(AQLPlan, on_delete=models.CASCADE, related_name="sampling_rows", verbose_name=_("الخطة"))
    code_letter = models.CharField(_("رمز الحرف"), max_length=2, db_index=True)
    sample_size = models.PositiveIntegerField(_("حجم العينة"))
    accept = models.PositiveIntegerField(_("عدد القبول (Ac)"), default=0)
    reject = models.PositiveIntegerField(_("عدد الرفض (Re)"), default=1)

    class Meta:
        verbose_name = _("صف عينة AQL")
        verbose_name_plural = _("صفوف عينات AQL")
        constraints = [
            models.UniqueConstraint(fields=["plan", "code_letter", "sample_size", "accept", "reject"], name="uq_aql_sampling_row"),
        ]
        indexes = [
            models.Index(fields=["plan", "code_letter"]),
        ]

    def __str__(self) -> str:
        return f"{self.plan} [{self.code_letter}] n={self.sample_size} Ac={self.accept}/Re={self.reject}"


class InspectionDecision(models.TextChoices):
    ACCEPT = "accept", _("قبول")
    REJECT = "reject", _("رفض")
    REWORK = "rework", _("إعادة عمل")
    CONTAIN = "contain", _("احتواء")


class InspectionLot(TimeStampedModel):
    """
    Executed AQL inspection instance: which lot, which plan, calculated code letter/sample size and the decision.
    """
    code = models.CharField(_("كود الفحص"), max_length=32, unique=True, db_index=True)

    stage = models.CharField(_("مرحلة الفحص"), max_length=16, choices=InspectionStage.choices, default=InspectionStage.INCOMING)
    plan = models.ForeignKey(AQLPlan, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("خطة AQL"))
    product = models.ForeignKey("products.Product", null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("المنتج"))
    inventory_item = models.ForeignKey("inventory.InventoryItem", null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("عنصر مخزون"))

    # Generic link to source doc (PO/WO/Shipment …)
    source_ct = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    source_id = models.PositiveIntegerField(null=True, blank=True)
    source = GenericForeignKey("source_ct", "source_id")
    source_ref = models.CharField(_("مرجع المستند"), max_length=128, null=True, blank=True)

    lot_size = models.PositiveIntegerField(_("حجم الدفعة"), db_index=True)
    code_letter = models.CharField(_("رمز الحرف"), max_length=2, null=True, blank=True)
    sample_size = models.PositiveIntegerField(_("حجم العينة"), null=True, blank=True)
    accept_number = models.PositiveIntegerField(_("عدد القبول (Ac)"), null=True, blank=True)
    reject_number = models.PositiveIntegerField(_("عدد الرفض (Re)"), null=True, blank=True)

    started_at = models.DateTimeField(_("بدأ في"), default=timezone.now)
    completed_at = models.DateTimeField(_("اكتمل في"), null=True, blank=True)
    decision = models.CharField(_("القرار"), max_length=12, choices=InspectionDecision.choices, null=True, blank=True)
    decision_reason = models.TextField(_("سبب القرار/ملاحظات"), null=True, blank=True)
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="qms_inspections", verbose_name=_("المفتش"))

    class Meta:
        verbose_name = _("دفعة فحص (AQL)")
        verbose_name_plural = _("دفعات الفحص (AQL)")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["stage", "decision"]),
            models.Index(fields=["product", "inventory_item"]),
            models.Index(fields=["lot_size"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.get_stage_display()}"

    @property
    def defects_total(self) -> int:
        return sum(self.results.values_list("defects_total", flat=True)) if hasattr(self, "results") else 0


class InspectionResult(TimeStampedModel):
    """
    Line-level results per inspected unit/sub-sample; allows both attribute & variable recording.
    """
    lot = models.ForeignKey(InspectionLot, on_delete=models.CASCADE, related_name="results", verbose_name=_("دفعة الفحص"))

    # Optional characteristic measurement (for variable type)
    characteristic = models.ForeignKey(QualityCharacteristic, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("خاصية جودة"))
    value = models.DecimalField(_("قيمة القياس"), max_digits=14, decimal_places=6, null=True, blank=True)

    # Attribute defects count by severity
    defects_critical = models.PositiveIntegerField(_("حرِجة"), default=0)
    defects_major = models.PositiveIntegerField(_("كبيرة"), default=0)
    defects_minor = models.PositiveIntegerField(_("ثانوية"), default=0)

    is_pass = models.BooleanField(_("مطابق؟"), default=True)

    class Meta:
        verbose_name = _("نتيجة فحص")
        verbose_name_plural = _("نتائج الفحص")
        indexes = [
            models.Index(fields=["is_pass"]),
        ]

    @property
    def defects_total(self) -> int:
        return (self.defects_critical or 0) + (self.defects_major or 0) + (self.defects_minor or 0)


class Nonconformity(TimeStampedModel):
    """
    Aggregated nonconformities found in an inspection lot, with typed defects.
    """
    lot = models.ForeignKey(InspectionLot, on_delete=models.CASCADE, related_name="nonconformities", verbose_name=_("دفعة الفحص"))
    defect_type = models.ForeignKey(DefectType, on_delete=models.PROTECT, verbose_name=_("نوع العيب"))
    count = models.PositiveIntegerField(_("العدد"), default=1)

    class Meta:
        verbose_name = _("لا مطابقة")
        verbose_name_plural = _("لا مطابقات")
        indexes = [
            models.Index(fields=["defect_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.defect_type} x {self.count}"


# -----------------------------
# SPC — Statistical Process Control
# -----------------------------

class ChartType(models.TextChoices):
    XBAR_R = "xbar_r", _("X̄-R")
    XBAR_S = "xbar_s", _("X̄-S")
    I_MR   = "i_mr", _("Individuals & MR")
    P      = "p", _("p (Proportion nonconforming)")
    NP     = "np", _("np (Count nonconforming)")
    C      = "c", _("c (Count of defects)")
    U      = "u", _("u (Defects per unit)")


class RuleSet(models.TextChoices):
    WESTERN_ELECTRIC = "weco", _("Western Electric")
    NELSON = "nelson", _("Nelson")
    BASIC_3SIGMA = "basic", _("±3σ basic")


class ControlProcess(TimeStampedModel):
    """
    A monitored process stream (product/operation-characteristic) under SPC.
    """
    key = models.CharField(_("كود العملية"), max_length=64, unique=True)
    name = models.CharField(_("اسم العملية"), max_length=255)

    product = models.ForeignKey("products.Product", null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("المنتج"))
    inventory_item = models.ForeignKey("inventory.InventoryItem", null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("عنصر مخزون"))
    characteristic = models.ForeignKey(QualityCharacteristic, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("خاصية جودة"))

    is_active = models.BooleanField(_("نشطة؟"), default=True)

    class Meta:
        verbose_name = _("عملية مراقبة (SPC)")
        verbose_name_plural = _("عمليات مراقبة (SPC)")
        indexes = [
            models.Index(fields=["key"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.key} — {self.name}"


class ControlChart(TimeStampedModel):
    """
    SPC chart configuration with current control limits. Limits may be system-calculated or manually set.
    """
    process = models.ForeignKey(ControlProcess, on_delete=models.CASCADE, related_name="charts", verbose_name=_("العملية"))
    chart_type = models.CharField(_("نوع المخطط"), max_length=16, choices=ChartType.choices, default=ChartType.XBAR_R)
    subgroup_size = models.PositiveIntegerField(_("حجم المجموعة الفرعية (n)"), default=5)
    rule_set = models.CharField(_("قواعد الكشف"), max_length=16, choices=RuleSet.choices, default=RuleSet.BASIC_3SIGMA)

    # Control limits
    cl = models.DecimalField(_("الحد المركزي (CL)"), max_digits=14, decimal_places=6, null=True, blank=True)
    ucl = models.DecimalField(_("الحد الأعلى (UCL)"), max_digits=14, decimal_places=6, null=True, blank=True)
    lcl = models.DecimalField(_("الحد الأدنى (LCL)"), max_digits=14, decimal_places=6, null=True, blank=True)
    auto_calculated = models.BooleanField(_("حُسِبت تلقائيًا؟"), default=True)

    effective_from = models.DateTimeField(_("ساري من"), default=timezone.now)
    is_active = models.BooleanField(_("نشط؟"), default=True)

    class Meta:
        verbose_name = _("مخطط ضبط إحصائي")
        verbose_name_plural = _("مخططات الضبط الإحصائي")
        indexes = [
            models.Index(fields=["chart_type", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.process} [{self.get_chart_type_display()}]"


class Subgroup(TimeStampedModel):
    """
    One subgroup (rational sample) under a ControlChart.
    """
    chart = models.ForeignKey(ControlChart, on_delete=models.CASCADE, related_name="subgroups", verbose_name=_("المخطط"))
    number = models.PositiveIntegerField(_("رقم المجموعة"), db_index=True)
    timestamp = models.DateTimeField(_("التاريخ/الوقت"), default=timezone.now)

    # Summary statistics (store for speed; can be recalculated by services)
    n = models.PositiveIntegerField(_("الحجم الفعلي"), default=0)
    mean = models.DecimalField(_("المتوسط (X̄)"), max_digits=14, decimal_places=6, null=True, blank=True)
    r = models.DecimalField(_("المدى (R)"), max_digits=14, decimal_places=6, null=True, blank=True)
    s = models.DecimalField(_("الانحراف المعياري (S)"), max_digits=14, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = _("مجموعة فرعية (Subgroup)")
        verbose_name_plural = _("مجموعات فرعية (Subgroups)")
        constraints = [
            models.UniqueConstraint(fields=["chart", "number"], name="uq_spc_chart_subgroup_number"),
        ]
        ordering = ["chart", "number"]

    def __str__(self) -> str:
        return f"{self.chart} — #{self.number}"


class DataPoint(TimeStampedModel):
    """
    Individual observation within a subgroup (for variable charts) or an attribute tally for p/np/c/u charts.
    """
    subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE, related_name="points", verbose_name=_("المجموعة الفرعية"))
    value = models.DecimalField(_("القيمة"), max_digits=14, decimal_places=6, null=True, blank=True)
    defects = models.PositiveIntegerField(_("عدد العيوب"), default=0)
    sample_size = models.PositiveIntegerField(_("حجم العينة للخصائص (Attribute)"), null=True, blank=True)

    is_out_of_control = models.BooleanField(_("خارج الضبط؟"), default=False)

    class Meta:
        verbose_name = _("نقطة بيانات")
        verbose_name_plural = _("نقاط البيانات")
        indexes = [
            models.Index(fields=["is_out_of_control"]),
        ]

    def __str__(self) -> str:
        return f"Point #{self.pk} — Subgroup {self.subgroup_id}"


class CapabilityStudy(TimeStampedModel):
    """
    Process capability/performance study for a defined window.
    """
    process = models.ForeignKey(ControlProcess, on_delete=models.CASCADE, related_name="capability_studies", verbose_name=_("العملية"))
    characteristic = models.ForeignKey(QualityCharacteristic, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("خاصية جودة"))

    period_from = models.DateTimeField(_("الفترة من"), null=True, blank=True)
    period_to = models.DateTimeField(_("الفترة إلى"), null=True, blank=True)

    # Specification limits (echoed for traceability)
    lsl = models.DecimalField(_("LSL"), max_digits=14, decimal_places=6, null=True, blank=True)
    usl = models.DecimalField(_("USL"), max_digits=14, decimal_places=6, null=True, blank=True)
    target = models.DecimalField(_("Target"), max_digits=14, decimal_places=6, null=True, blank=True)

    # Capability indices (store snapshot)
    cp  = models.DecimalField(_("Cp"),  max_digits=10, decimal_places=4, null=True, blank=True)
    cpk = models.DecimalField(_("Cpk"), max_digits=10, decimal_places=4, null=True, blank=True)
    pp  = models.DecimalField(_("Pp"),  max_digits=10, decimal_places=4, null=True, blank=True)
    ppk = models.DecimalField(_("Ppk"), max_digits=10, decimal_places=4, null=True, blank=True)

    sample_count = models.PositiveIntegerField(_("عدد العينات"), default=0)

    class Meta:
        verbose_name = _("دراسة قابلية العملية")
        verbose_name_plural = _("دراسات قابلية العملية")
        ordering = ["-created_at"]


# -----------------------------
# CAPA — Corrective & Preventive Actions
# -----------------------------

class CAPAType(models.TextChoices):
    CORRECTIVE = "cor", _("تصحيحية")
    PREVENTIVE = "pre", _("وقائية")


class CAPAStatus(models.TextChoices):
    OPEN = "open", _("مفتوحة")
    IN_PROGRESS = "in_progress", _("قيد التنفيذ")
    IMPLEMENTED = "implemented", _("تم التنفيذ")
    VERIFIED = "verified", _("تم التحقق")
    INEFFECTIVE = "ineffective", _("غير فعالة")
    CLOSED = "closed", _("مغلقة")


class RootCauseMethod(models.TextChoices):
    FIVE_WHYS = "5whys", _("5 Whys")
    FISHBONE = "fishbone", _("عظم السمكة (Ishikawa)")
    RCA = "rca", _("تحليل السبب الجذري (RCA)")


class CAPARecord(TimeStampedModel):
    """
    CAPA record aligned with 8D elements (without enforcing the entire template).
    """
    code = models.CharField(_("كود CAPA"), max_length=32, unique=True, db_index=True)
    title = models.CharField(_("العنوان"), max_length=255)
    capa_type = models.CharField(_("النوع"), max_length=3, choices=CAPAType.choices, default=CAPAType.CORRECTIVE)
    status = models.CharField(_("الحالة"), max_length=16, choices=CAPAStatus.choices, default=CAPAStatus.OPEN)

    # Source link: inspection, audit, complaint, NCR, etc.
    source_ct = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    source_id = models.PositiveIntegerField(null=True, blank=True)
    source = GenericForeignKey("source_ct", "source_id")
    source_ref = models.CharField(_("مرجع المصدر"), max_length=128, null=True, blank=True)

    # Risk metrics (FMEA-like)
    severity = models.PositiveSmallIntegerField(_("الخطورة (S)"), null=True, blank=True)
    occurrence = models.PositiveSmallIntegerField(_("التكرار (O)"), null=True, blank=True)
    detection = models.PositiveSmallIntegerField(_("الاكتشاف (D)"), null=True, blank=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="capa_owned", verbose_name=_("المالك"))
    due_date = models.DateField(_("تاريخ الاستحقاق"), null=True, blank=True)

    root_cause_method = models.CharField(_("منهجية السبب الجذري"), max_length=16, choices=RootCauseMethod.choices, null=True, blank=True)
    root_cause = models.TextField(_("السبب الجذري"), null=True, blank=True)
    containment = models.TextField(_("إجراءات الاحتواء (سريعة)"), null=True, blank=True)

    effectiveness_verified_at = models.DateTimeField(_("تاريخ التحقق من الفاعلية"), null=True, blank=True)
    effectiveness_verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="capa_verified", verbose_name=_("مُتحقق"))

    attachments = models.JSONField(_("مرفقات (روابط/معرّفات)"), default=dict, blank=True)

    class Meta:
        verbose_name = _("سجل CAPA")
        verbose_name_plural = _("سجلات CAPA")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.title}"

    @property
    def rpn(self) -> int | None:
        if self.severity and self.occurrence and self.detection:
            return int(self.severity) * int(self.occurrence) * int(self.detection)
        return None


class CAPAAction(TimeStampedModel):
    """
    Discrete action under a CAPA record (corrective or preventive).
    """
    record = models.ForeignKey(CAPARecord, on_delete=models.CASCADE, related_name="actions", verbose_name=_("سجل CAPA"))
    action_type = models.CharField(_("نوع الإجراء"), max_length=3, choices=CAPAType.choices, default=CAPAType.CORRECTIVE)
    description = models.TextField(_("الوصف"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="capa_actions", verbose_name=_("المسؤول"))
    due_date = models.DateField(_("تاريخ الاستحقاق"), null=True, blank=True)
    status = models.CharField(_("الحالة"), max_length=16, choices=CAPAStatus.choices, default=CAPAStatus.OPEN)

    implemented_at = models.DateTimeField(_("تاريخ التنفيذ"), null=True, blank=True)
    verified_at = models.DateTimeField(_("تاريخ التحقق"), null=True, blank=True)
    verification_result = models.CharField(_("نتيجة التحقق"), max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = _("إجراء CAPA")
        verbose_name_plural = _("إجراءات CAPA")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.record.code} — {self.get_action_type_display()}"


# -----------------------------
# Signals / Code Generation
# -----------------------------

from django.db.models.signals import pre_save
from django.dispatch import receiver

def _generate_code(prefix: str) -> str:
    today = timezone.localdate()
    stamp = today.strftime("%Y%m")
    # A simple sequence using last code in month (safe for low concurrency; for high, use DB sequences/locks)
    base = f"{prefix}-{stamp}-"
    last = (
        InspectionLot.objects.filter(code__startswith=base)
        .order_by("-code")
        .values_list("code", flat=True)
        .first()
        if prefix == "QMS-INSP" else
        CAPARecord.objects.filter(code__startswith=base).order_by("-code").values_list("code", flat=True).first()
    )
    seq = 1
    if last:
        try:
            seq = int(last.split("-")[-1]) + 1
        except Exception:
            seq = 1
    return f"{base}{seq:04d}"

@receiver(pre_save, sender=InspectionLot)
def qms_inspectionlot_presave(sender, instance: InspectionLot, **kwargs):
    if not instance.code:
        instance.code = _generate_code("QMS-INSP")

@receiver(pre_save, sender=CAPARecord)
def qms_capa_presave(sender, instance: CAPARecord, **kwargs):
    if not instance.code:
        instance.code = _generate_code("QMS-CAPA")
