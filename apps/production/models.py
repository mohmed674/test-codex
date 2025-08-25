from django.db import models
from apps.employees.models import Employee
from apps.products.models import FinishedProduct  # ← ✅ تم التعديل
from apps.inventory.models import RawMaterial
from django.utils import timezone


# -----------------------------------
# أوامر التشغيل
# -----------------------------------
class ProductionOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('in_progress', 'جاري التصنيع'),
        ('completed', 'تم الانتهاء'),
        ('cancelled', 'ملغاة'),
    )

    order_number = models.CharField(max_length=20, unique=True)
    product = models.ForeignKey(FinishedProduct, on_delete=models.CASCADE)  # ← هنا التعديل
    quantity = models.PositiveIntegerField()
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"أمر تشغيل {self.order_number} - {self.product.name}"

# -----------------------------------
# مراحل التصنيع
# -----------------------------------
class ProductionStage(models.Model):
    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='stages')
    stage_name = models.CharField(max_length=100)
    assigned_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    observations = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.stage_name} - {self.order.order_number}"

# -----------------------------------
# استهلاك المواد الخام
# -----------------------------------
class MaterialConsumption(models.Model):
    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='materials_used')
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)  # كجم، متر، سم
    wastage = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # الهالك

    def __str__(self):
        return f"{self.material.name} - {self.order.order_number}"

# -----------------------------------
# الإنتاج النهائي
# -----------------------------------
class FinalProductOutput(models.Model):
    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='outputs')
    quantity_produced = models.PositiveIntegerField()
    produced_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"إنتاج نهائي - {self.order.order_number}"

# -----------------------------------
# تتبع QR أثناء التصنيع
# -----------------------------------
class ProductionScanQR(models.Model):
    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE)
    scan_time = models.DateTimeField(auto_now_add=True)
    scanned_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    qr_data = models.TextField()  # محتوى QR كبيانات التتبع

    def __str__(self):
        return f"QR - {self.order.order_number} - {self.scan_time.strftime('%Y-%m-%d %H:%M')}"

# -----------------------------------
# ✅ نموذج الخامات (Bill Of Materials)
# -----------------------------------
class BillOfMaterials(models.Model):
    product = models.ForeignKey(FinishedProduct, on_delete=models.CASCADE, verbose_name="المنتج النهائي")
    components = models.JSONField(verbose_name="المكونات")  
    # مثال: [{"item": "قماش", "quantity": 10, "unit": "متر"}]
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نموذج تصنيع"
        verbose_name_plural = "نماذج التصنيع"

    def __str__(self):
        return f"نموذج تصنيع لـ {self.product.name}"

# -----------------------------------
# ✅ فحوصات الجودة
# -----------------------------------
QUALITY_STATUS_CHOICES = [
    ("pending", "قيد الفحص"),
    ("passed", "مطابق"),
    ("failed", "مرفوض"),
]

class QualityCheck(models.Model):
    product = models.ForeignKey(FinishedProduct, on_delete=models.CASCADE, verbose_name="المنتج")  # ← هنا التعديل
    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, verbose_name="أمر التشغيل")
    stage = models.ForeignKey(ProductionStage, on_delete=models.CASCADE, verbose_name="مرحلة الإنتاج")
    inspector = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المفتش")
    status = models.CharField(max_length=20, choices=QUALITY_STATUS_CHOICES, default="pending", verbose_name="الحالة")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات الفحص")
    inspected_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الفحص")

    class Meta:
        verbose_name = "فحص جودة"
        verbose_name_plural = "فحوصات الجودة"
        ordering = ['-inspected_at']

    def __str__(self):
        return f"{self.product.name} - {self.stage.stage_name} - {self.status}"

# -----------------------------------
# ✅ إدارة دورة حياة المنتج (PLM)
# -----------------------------------
class ProductVersion(models.Model):
    product = models.ForeignKey(FinishedProduct, on_delete=models.CASCADE, verbose_name="المنتج")  # ← هنا التعديل
    version_code = models.CharField(max_length=20, verbose_name="كود النسخة")
    season = models.CharField(max_length=100, blank=True, null=True, verbose_name="الموسم (صيف - شتاء...)")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="أنشئ بواسطة")
    change_notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات التعديل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")

    class Meta:
        verbose_name = "نسخة منتج"
        verbose_name_plural = "دورة حياة المنتج"
        unique_together = ('product', 'version_code')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - إصدار {self.version_code}"


# -----------------------------------
# سجل الإنتاج (Production Log)
# -----------------------------------
class ProductionLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, null=True, blank=True)
    stage = models.ForeignKey(ProductionStage, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    quantity = models.PositiveIntegerField(default=0)
    unit_wage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee} - {self.quantity} - {self.date}"
