from io import BytesIO
# pylint: disable=no-member
from django.core.files import File
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
try:
    import qrcode  # type: ignore
except Exception:  # pragma: no cover
    qrcode = None


def _build_qr_png(data: str) -> BytesIO:
    if not qrcode:
        return BytesIO()
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf


class ActiveQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def search(self, term: str):
        t = (term or "").strip()
        if not t:
            return self
        return self.filter(models.Q(name__icontains=t) | models.Q(code__icontains=t))


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم المنتج")
    code = models.CharField(max_length=100, unique=True, verbose_name="كود المنتج")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="السعر")
    is_active = models.BooleanField(default=True, verbose_name="نشط؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    barcode = models.CharField(max_length=64, blank=True, null=True, db_index=True, verbose_name="الباركود/GTIN")
    uom = models.CharField(max_length=32, default="pcs", verbose_name="وحدة القياس")
    currency = models.CharField(max_length=3, default="EGP", verbose_name="العملة (ISO4217)")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="التكلفة التقديرية")
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="نسبة الضريبة %"
    )
    attributes = models.JSONField(default=dict, blank=True, verbose_name="خصائص/سمات (JSON)")
    slug = models.SlugField(max_length=220, blank=True, verbose_name="Slug (اختياري)")
    image = models.ImageField(upload_to="product_images/", blank=True, null=True, verbose_name="صورة المنتج")
    qr_code = models.ImageField(upload_to="product_qrcodes/", blank=True, null=True, verbose_name="QR كود")

    objects = ActiveQuerySet.as_manager()

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["name"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def margin(self):
        try:
            return (self.price or 0) - (self.cost_price or 0)
        except Exception:
            return 0

    @property
    def margin_percent(self):
        try:
            if (self.price or 0) == 0:
                return 0
            return round((self.margin / self.price) * 100, 2)
        except Exception:
            return 0

    def get_absolute_url(self):
        try:
            return reverse("products:product_detail", kwargs={"code": self.code})
        except Exception:
            return "#"

    def _qr_payload(self) -> str:
        return (
            f"TYPE=RAW\n"
            f"NAME={self.name}\n"
            f"CODE={self.code}\n"
            f"UOM={self.uom}\n"
            f"PRICE={self.price}\n"
            f"COST={self.cost_price}\n"
            f"MARGIN={self.margin}\n"
            f"CURRENCY={self.currency}\n"
            f"BARCODE={self.barcode or ''}\n"
        )

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)[:220]

        should_regen_qr = False
        if self.pk:
            try:
                prev = type(self).objects.only(
                    "name", "code", "uom", "price", "cost_price", "currency", "barcode"
                ).get(pk=self.pk)
                fields_to_watch = ["name", "code", "uom", "price", "cost_price", "currency", "barcode"]
                should_regen_qr = any(getattr(prev, f) != getattr(self, f) for f in fields_to_watch)
            except type(self).DoesNotExist:
                should_regen_qr = True
        else:
            should_regen_qr = True

        super().save(*args, **kwargs)

        if should_regen_qr:
            payload = self._qr_payload()
            buf = _build_qr_png(payload)
            fname = f"{self.code}_qr.png"
            self.qr_code.save(fname, File(buf), save=False)
            super().save(update_fields=["qr_code"])


QUALITY_STATUS_CHOICES = (
    ("good", "جيد"),
    ("average", "مقبول"),
    ("rejected", "مرفوض"),
)


class FinishedProduct(models.Model):
    inventory_item = models.ForeignKey(
        "inventory.InventoryItem",
        on_delete=models.CASCADE,
        related_name="finished_products",
        verbose_name="الصنف المرتبط",
    )
    product_code = models.CharField(max_length=100, unique=True, verbose_name="كود المنتج")
    name = models.CharField(max_length=100, verbose_name="اسم المنتج")
    quantity = models.PositiveIntegerField(verbose_name="الكمية")
    date_produced = models.DateField(default=timezone.now, verbose_name="تاريخ الإنتاج")
    image = models.ImageField(upload_to="product_images/", blank=True, null=True, verbose_name="صورة المنتج")
    quality_status = models.CharField(
        max_length=10, choices=QUALITY_STATUS_CHOICES, default="good", verbose_name="حالة الجودة"
    )
    expiration_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الانتهاء (اختياري)")
    qr_code = models.ImageField(upload_to="product_qrcodes/", blank=True, null=True, verbose_name="QR كود")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    batch_number = models.CharField(max_length=64, blank=True, null=True, verbose_name="رقم التشغيل/الدفعة")
    lot = models.CharField(max_length=64, blank=True, null=True, verbose_name="LOT")
    location_code = models.CharField(max_length=64, blank=True, null=True, verbose_name="موقع التخزين (رمز)")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات داخلية")
    attributes = models.JSONField(default=dict, blank=True, verbose_name="خصائص/سمات (JSON)")

    class Meta:
        verbose_name = "المنتج النهائي"
        verbose_name_plural = "المنتجات النهائية"
        ordering = ["-date_produced"]
        indexes = [
            models.Index(fields=["product_code"]),
            models.Index(fields=["date_produced"]),
            models.Index(fields=["quality_status"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.product_code}"

    @property
    def is_expired(self) -> bool:
        return bool(self.expiration_date and self.expiration_date < timezone.now().date())

    def clean(self):
        if self.expiration_date and self.date_produced and self.expiration_date < self.date_produced:
            from django.core.exceptions import ValidationError
            raise ValidationError({"expiration_date": "تاريخ الانتهاء يجب أن يكون بعد/يساوي تاريخ الإنتاج."})

    def _qr_payload(self) -> str:
        return (
            f"TYPE=FINISHED\n"
            f"NAME={self.name}\n"
            f"CODE={self.product_code}\n"
            f"QTY={self.quantity}\n"
            f"DATE={self.date_produced.isoformat() if self.date_produced else ''}\n"
            f"QUALITY={self.quality_status}\n"
            f"BATCH={self.batch_number or ''}\n"
            f"LOT={self.lot or ''}\n"
            f"LOC={self.location_code or ''}\n"
            f"EXPIRES={self.expiration_date.isoformat() if self.expiration_date else ''}\n"
        )

    def save(self, *args, **kwargs):
        should_regen_qr = False
        if self.pk:
            try:
                prev = type(self).objects.only(
                    "name", "product_code", "quantity", "date_produced", "quality_status",
                    "expiration_date", "batch_number", "lot", "location_code"
                ).get(pk=self.pk)
                watch = [
                    "name", "product_code", "quantity", "date_produced", "quality_status",
                    "expiration_date", "batch_number", "lot", "location_code"
                ]
                should_regen_qr = any(getattr(prev, f) != getattr(self, f) for f in watch)
            except type(self).DoesNotExist:
                should_regen_qr = True
        else:
            should_regen_qr = True

        super().save(*args, **kwargs)

        if should_regen_qr or not self.qr_code:
            payload = self._qr_payload()
            buf = _build_qr_png(payload)
            fname = f"{self.product_code}_qr.png"
            self.qr_code.save(fname, File(buf), save=False)
            super().save(update_fields=["qr_code"])
