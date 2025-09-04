from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, cast

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.products.models import FinishedProduct

# ✅ خيارات وحدات القياس (cast لضمان type safety)
UNIT_CHOICES: list[tuple[str, str]] = [
    ("pcs", cast(str, _("قطعة"))),
    ("kg", cast(str, _("كيلو"))),
    ("m", cast(str, _("متر"))),
    ("roll", cast(str, _("رول"))),
    ("box", cast(str, _("علبة"))),
]
UNIT_LABELS: Dict[str, str] = {k: str(v) for k, v in UNIT_CHOICES}

# ✅ أنواع حركة المخزون
MOVEMENT_TYPE_CHOICES: list[tuple[str, str]] = [
    ("in", cast(str, _("دخول"))),
    ("out", cast(str, _("خروج"))),
    ("adjust", cast(str, _("تسوية"))),
]
MOVEMENT_TYPE_LABELS: Dict[str, str] = {k: str(v) for k, v in MOVEMENT_TYPE_CHOICES}

# ✅ أنواع الجرد
INVENTORY_TYPES: list[tuple[str, str]] = [
    ("weekly", cast(str, _("جرد جزئي أسبوعي"))),
    ("monthly", cast(str, _("جرد شهري"))),
    ("annual", cast(str, _("جرد سنوي"))),
]
INVENTORY_TYPE_LABELS: Dict[str, str] = {k: str(v) for k, v in INVENTORY_TYPES}


# ---------------------------------------------------
# 🧵 0. المواد الخام (RawMaterial)
# ---------------------------------------------------
class RawMaterial(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("الاسم"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("الكود"))
    unit = models.CharField(
        max_length=20, choices=UNIT_CHOICES, default="kg", verbose_name=_("وحدة القياس")
    )
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))

    class Meta:
        verbose_name = _("مادة خام")
        verbose_name_plural = _("المواد الخام")

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------
# 🏢 1. نموذج المخزن
# ---------------------------------------------------
class Warehouse(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("اسم المخزن"))
    location = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("الموقع")
    )
    manager = models.CharField(max_length=100, blank=True, verbose_name=_("المدير"))
    note = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))

    class Meta:
        verbose_name = _("مخزن")
        verbose_name_plural = _("المخازن")

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------
# 📦 2. عنصر المخزون داخل المخزن
# ---------------------------------------------------
class InventoryItem(models.Model):
    product = models.ForeignKey(
        FinishedProduct, on_delete=models.CASCADE, verbose_name=_("المنتج")
    )
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, verbose_name=_("المخزن")
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("الكمية")
    )
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default="pcs",
        verbose_name=_("وحدة القياس"),
    )
    min_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("الحد الأدنى"),
    )
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))

    class Meta:
        unique_together = ["product", "warehouse"]
        verbose_name = _("عنصر مخزون")
        verbose_name_plural = _("عناصر المخزون")

    def is_below_threshold(self) -> bool:
        return self.quantity < self.min_threshold

    def __str__(self) -> str:
        unit_label = UNIT_LABELS.get(self.unit, self.unit)
        try:
            return f"{self.product.name} – {self.quantity} {unit_label} في {self.warehouse.name}"
        except Exception:
            return f"{self.quantity} {unit_label}"


# ---------------------------------------------------
# 🔄 3. حركة المخزون (دخول - خروج - تسوية)
# ---------------------------------------------------
class InventoryMovement(models.Model):
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="movements",
        verbose_name=_("العنصر"),
    )
    movement_type = models.CharField(
        max_length=10, choices=MOVEMENT_TYPE_CHOICES, verbose_name=_("نوع الحركة")
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("الكمية")
    )
    date = models.DateTimeField(default=timezone.now, verbose_name=_("التاريخ"))
    note = models.TextField(blank=True, null=True, verbose_name=_("ملاحظة"))

    class Meta:
        ordering = ["-date"]
        verbose_name = _("حركة مخزون")
        verbose_name_plural = _("حركات المخزون")

    def __str__(self) -> str:
        label = MOVEMENT_TYPE_LABELS.get(self.movement_type, self.movement_type)
        try:
            return f"{self.item.product.name} - {label} - {self.quantity}"
        except Exception:
            return f"{label} - {self.quantity}"


# ---------------------------------------------------
# 📋 4. سجل الجرد الفعلي (الذكي)
# ---------------------------------------------------
class InventoryAudit(models.Model):
    audit_type = models.CharField(
        max_length=20, choices=INVENTORY_TYPES, verbose_name=_("نوع الجرد")
    )
    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name=_("تم بواسطة")
    )
    performed_at = models.DateTimeField(
        default=timezone.now, verbose_name=_("تاريخ الجرد")
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))

    class Meta:
        verbose_name = _("جرد فعلي")
        verbose_name_plural = _("جرد فعلي")

    def __str__(self) -> str:
        label = INVENTORY_TYPE_LABELS.get(self.audit_type, self.audit_type)
        return f"{label} - {self.performed_at.date()}"


# ---------------------------------------------------
# 🧾 5. تفاصيل الجرد الفعلي لكل صنف
# ---------------------------------------------------
class InventoryAuditItem(models.Model):
    audit = models.ForeignKey(
        InventoryAudit,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("الجرد"),
    )
    product = models.ForeignKey(
        FinishedProduct, on_delete=models.CASCADE, verbose_name=_("المنتج")
    )
    system_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("كمية النظام")
    )
    physical_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("الكمية الفعلية")
    )
    difference = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("الفرق"),
    )
    remarks = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))

    class Meta:
        verbose_name = _("تفاصيل الجرد")
        verbose_name_plural = _("تفاصيل الجرد")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.difference = self.physical_quantity - self.system_quantity
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.product.name} — Δ {self.difference}"


# ---------------------------------------------------
# 🚨 6. تحقيق داخلي في الفروقات الكبيرة
# ---------------------------------------------------
class InventoryDiscrepancyInvestigation(models.Model):
    audit_item = models.OneToOneField(
        InventoryAuditItem, on_delete=models.CASCADE, verbose_name=_("عنصر الجرد")
    )
    is_resolved = models.BooleanField(default=False, verbose_name=_("تم الحل"))
    action_taken = models.TextField(
        blank=True, null=True, verbose_name=_("الإجراء المتخذ")
    )
    reported_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="discrepancy_reports",
        verbose_name=_("تم التبليغ إلى"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإنشاء")
    )

    class Meta:
        verbose_name = _("تحقيق في فروقات الجرد")
        verbose_name_plural = _("تحقيقات فروقات الجرد")

    def __str__(self) -> str:
        return f"تحقيق في فرق الجرد - {self.audit_item.product.name}"


# ---------------------------------------------------
# 🪪 Proxy Model (واضح وآمن)
# ---------------------------------------------------
class Inventory(InventoryItem):
    """Proxy باسم مختصر "Inventory" بدون إعادة تعريف الكيان."""

    class Meta:
        proxy = True
        verbose_name = _("Inventory")
        verbose_name_plural = _("Inventory")
