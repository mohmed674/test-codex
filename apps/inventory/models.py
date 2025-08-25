from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from apps.products.models import FinishedProduct
from django.utils.translation import gettext_lazy as _

# ✅ خيارات وحدات القياس
UNIT_CHOICES = [
    ('pcs', _('قطعة')),
    ('kg', _('كيلو')),
    ('m', _('متر')),
    ('roll', _('رول')),
    ('box', _('علبة')),
]

# ✅ أنواع حركة المخزون
MOVEMENT_TYPE_CHOICES = [
    ('in', _('دخول')),
    ('out', _('خروج')),
    ('adjust', _('تسوية')),
]

# ✅ أنواع الجرد
INVENTORY_TYPES = [
    ('weekly', _('جرد جزئي أسبوعي')),
    ('monthly', _('جرد شهري')),
    ('annual', _('جرد سنوي')),
]

# ---------------------------------------------------
# 🧵 0. المواد الخام (RawMaterial)
# ---------------------------------------------------
class RawMaterial(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("الاسم"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("الكود"))
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg', verbose_name=_("وحدة القياس"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))

    class Meta:
        verbose_name = _("مادة خام")
        verbose_name_plural = _("المواد الخام")

    def __str__(self):
        return self.name

# ---------------------------------------------------
# 🏢 1. نموذج المخزن
# ---------------------------------------------------
class Warehouse(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("اسم المخزن"))
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("الموقع"))
    manager = models.CharField(max_length=100, blank=True, verbose_name=_("المدير"))
    note = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))

    class Meta:
        verbose_name = _("مخزن")
        verbose_name_plural = _("المخازن")

    def __str__(self):
        return self.name

# ---------------------------------------------------
# 📦 2. عنصر المخزون داخل المخزن
# ---------------------------------------------------
class InventoryItem(models.Model):
    product = models.ForeignKey(FinishedProduct, on_delete=models.CASCADE, verbose_name=_("المنتج"))
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name=_("المخزن"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("الكمية"))
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs', verbose_name=_("وحدة القياس"))
    min_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("الحد الأدنى"))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))

    class Meta:
        unique_together = ['product', 'warehouse']
        verbose_name = _("عنصر مخزون")
        verbose_name_plural = _("عناصر المخزون")

    def is_below_threshold(self):
        return self.quantity < self.min_threshold

    def __str__(self):
        try:
            return f"{self.product.name} – {self.quantity} {self.get_unit_display()} في {self.warehouse.name}"
        except Exception:
            return f"{self.quantity} {self.get_unit_display()} في {self.warehouse.name}"

# ---------------------------------------------------
# 🔄 3. حركة المخزون (دخول - خروج - تسوية)
# ---------------------------------------------------
class InventoryMovement(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements', verbose_name=_("العنصر"))
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPE_CHOICES, verbose_name=_("نوع الحركة"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("الكمية"))
    date = models.DateTimeField(default=timezone.now, verbose_name=_("التاريخ"))
    note = models.TextField(blank=True, null=True, verbose_name=_("ملاحظة"))

    class Meta:
        ordering = ['-date']
        verbose_name = _("حركة مخزون")
        verbose_name_plural = _("حركات المخزون")

    def __str__(self):
        try:
            return f"{self.item.product.name} - {self.get_movement_type_display()} - {self.quantity}"
        except Exception:
            return f"{self.get_movement_type_display()} - {self.quantity}"

# ---------------------------------------------------
# 📋 4. سجل الجرد الفعلي (الذكي)
# ---------------------------------------------------
class InventoryAudit(models.Model):
    audit_type = models.CharField(max_length=20, choices=INVENTORY_TYPES, verbose_name=_("نوع الجرد"))
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("تم بواسطة"))
    performed_at = models.DateTimeField(default=timezone.now, verbose_name=_("تاريخ الجرد"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))

    class Meta:
        verbose_name = _("جرد فعلي")
        verbose_name_plural = _("جرد فعلي")

    def __str__(self):
        return f"{self.get_audit_type_display()} - {self.performed_at.date()}"

# ---------------------------------------------------
# 🧾 5. تفاصيل الجرد الفعلي لكل صنف
# ---------------------------------------------------
class InventoryAuditItem(models.Model):
    audit = models.ForeignKey(InventoryAudit, on_delete=models.CASCADE, related_name="items", verbose_name=_("الجرد"))
    product = models.ForeignKey(FinishedProduct, on_delete=models.CASCADE, verbose_name=_("المنتج"))
    system_quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("كمية النظام"))
    physical_quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("الكمية الفعلية"))
    difference = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("الفرق"))
    remarks = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))

    class Meta:
        verbose_name = _("تفاصيل الجرد")
        verbose_name_plural = _("تفاصيل الجرد")

    def save(self, *args, **kwargs):
        self.difference = self.physical_quantity - self.system_quantity
        super().save(*args, **kwargs)

# ---------------------------------------------------
# 🚨 6. تحقيق داخلي في الفروقات الكبيرة
# ---------------------------------------------------
class InventoryDiscrepancyInvestigation(models.Model):
    audit_item = models.OneToOneField(InventoryAuditItem, on_delete=models.CASCADE, verbose_name=_("عنصر الجرد"))
    is_resolved = models.BooleanField(default=False, verbose_name=_("تم الحل"))
    action_taken = models.TextField(blank=True, null=True, verbose_name=_("الإجراء المتخذ"))
    reported_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='discrepancy_reports', verbose_name=_("تم التبليغ إلى"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))

    class Meta:
        verbose_name = _("تحقيق في فروقات الجرد")
        verbose_name_plural = _("تحقيقات فروقات الجرد")

    def __str__(self):
        return f"تحقيق في فرق الجرد - {self.audit_item.product.name}"

# ---- AUTO ALIAS (Proxy) ----
try:
    from .models import InventoryItem  # self-import guard if file split; fallback below
except Exception:
    pass

try:
    class Inventory(InventoryItem):  # proxy alias to satisfy imports
        class Meta:
            proxy = True
            verbose_name = "Inventory"
            verbose_name_plural = "Inventory"
except NameError:
    # Fallback when in same file scope
    class Inventory(InventoryItem):  # type: ignore[name-defined]
        class Meta:
            proxy = True
            verbose_name = "Inventory"
            verbose_name_plural = "Inventory"
# ---- END AUTO ALIAS ----
