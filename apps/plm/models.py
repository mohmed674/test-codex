from django.db import models


class PLMDocument(models.Model):
    """مستند عام داخل دورة حياة المنتج"""
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50, default='v1.0')
    file = models.FileField(upload_to='plm/docs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'PLM Document'
        verbose_name_plural = 'PLM Documents'

    def __str__(self):
        return f"{self.name} ({self.version})"


class ProductTemplate(models.Model):
    """تعريف المنتج الأساسي (Template)"""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=120, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    uom = models.CharField(max_length=32, default='pcs')  # وحدة القياس
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class ProductVersion(models.Model):
    """نسخة المنتج (كل تغيير في الباترون/الخامات)"""
    STATUS_CHOICES = (
        ('draft', 'مسودة'),
        ('in_review', 'قيد المراجعة'),
        ('approved', 'معتمد'),
        ('archived', 'مؤرشف'),
    )

    product = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE, related_name='versions')
    version_code = models.CharField(max_length=50, default='v1.0')
    title = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    effective_from = models.DateField(blank=True, null=True)
    effective_to = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    documents = models.ManyToManyField(PLMDocument, blank=True, related_name='product_versions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('product', 'version_code'),)
        ordering = ['product__code', 'version_code']
        indexes = [
            models.Index(fields=['version_code']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.product.code} - {self.version_code}"


class LifecycleStage(models.Model):
    """المراحل (تصميم – مراجعة – إنتاج – إلخ)"""
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class ProductLifecycle(models.Model):
    """المنتج مرتبط بمراحل الدورة"""
    product = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE, related_name='lifecycles')
    stage = models.ForeignKey(LifecycleStage, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} → {self.stage.name}"


class Bom(models.Model):
    """رأس شجرة المواد (BOM) لنسخة المنتج"""
    product_version = models.ForeignKey(ProductVersion, on_delete=models.CASCADE, related_name='boms')
    code = models.CharField(max_length=60, default='BOM-1')
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('product_version', 'code'),)
        indexes = [models.Index(fields=['code']), models.Index(fields=['is_active'])]

    def __str__(self):
        return f"{self.product_version} / {self.code}"


class BomLine(models.Model):
    """عناصر شجرة المواد"""
    bom = models.ForeignKey(Bom, on_delete=models.CASCADE, related_name='lines')
    component = models.ForeignKey(ProductTemplate, on_delete=models.PROTECT, related_name='as_component_in_boms')
    description = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    uom = models.CharField(max_length=32, default='pcs')
    wastage_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # نسبة الهالك
    operation = models.CharField(max_length=120, blank=True, null=True)  # مرحلة الاستخدام (قص/خياطة...)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.bom.code} → {self.component.code} x {self.quantity} {self.uom}"


class ChangeRequest(models.Model):
    """طلب تغيير/أمر تغيير هندسي ECO"""
    TYPE_CHOICES = (
        ('design', 'تصميم'),
        ('material', 'خامة'),
        ('process', 'عملية تصنيع'),
        ('packaging', 'تعبئة وتغليف'),
        ('other', 'أخرى'),
    )
    STATUS_CHOICES = (
        ('draft', 'مسودة'),
        ('submitted', 'مرفوع'),
        ('approved', 'معتمد'),
        ('rejected', 'مرفوض'),
        ('implemented', 'منفذ'),
        ('canceled', 'ملغي'),
    )

    number = models.CharField(max_length=40, unique=True)
    product = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE, related_name='change_requests')
    from_version = models.ForeignKey(ProductVersion, on_delete=models.PROTECT, related_name='cr_from', blank=True, null=True)
    to_version = models.ForeignKey(ProductVersion, on_delete=models.PROTECT, related_name='cr_to', blank=True, null=True)
    change_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='design')
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    requested_by = models.CharField(max_length=150, blank=True, null=True)
    approved_by = models.CharField(max_length=150, blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    implemented_at = models.DateTimeField(blank=True, null=True)
    attachments = models.ManyToManyField(PLMDocument, blank=True, related_name='change_requests')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['status']),
            models.Index(fields=['change_type']),
        ]

    def __str__(self):
        return f"ECO {self.number} - {self.product.code}"


class ChangeRequestItem(models.Model):
    """تفاصيل العناصر المتأثرة في طلب التغيير"""
    change_request = models.ForeignKey(ChangeRequest, on_delete=models.CASCADE, related_name='items')
    bom = models.ForeignKey(Bom, on_delete=models.PROTECT, related_name='change_items', blank=True, null=True)
    bom_line = models.ForeignKey(BomLine, on_delete=models.PROTECT, related_name='change_items', blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.change_request.number} item"
