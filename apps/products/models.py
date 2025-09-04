from io import BytesIO
from decimal import Decimal
from typing import Optional, cast

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.pil import PilImage
from PIL.Image import Image as PILImage

from django.core.files import File
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


def _build_qr_png(data: str) -> BytesIO:
    """يبني صورة QR كـ PNG ويعيد Buffer."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,  # استيراد ثابت لتفادي تحذير "qrcode.constants"
        box_size=8,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # qrcode.make_image قد يُرجع PilImage أو أنواع أخرى (_DefaultImage / PyPNGImage).
    # نستخدم getattr للحصول على صورة PIL الحقيقية إن وُجدت، وإلا نستخدم الكائن نفسه.
    img_obj = qr.make_image(fill_color="black", back_color="white")
    pil_img: PILImage = cast(PILImage, getattr(img_obj, "get_image", lambda: img_obj)())

    buf = BytesIO()
    # PIL.Image.save يدعم format/optimize لـ PNG
    pil_img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf


class ActiveQuerySet(models.QuerySet):
    def active(self) -> "ActiveQuerySet":
        return self.filter(is_active=True)

    def search(self, term: str) -> "ActiveQuerySet":
        t = (term or "").strip()
        if not t:
            return self
        return self.filter(models.Q(name__icontains=t) | models.Q(code__icontains=t))


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم المنتج")
    code = models.CharField(max_length=100, unique=True, verbose_name="كود المنتج")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0"), verbose_name="السعر"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    barcode = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="الباركود/GTIN",
    )
    uom = models.CharField(max_length=32, default="pcs", verbose_name="وحدة القياس")
    currency = models.CharField(
        max_length=3, default="EGP", verbose_name="العملة (ISO4217)"
    )
    cost_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0"), verbose_name="التكلفة التقديرية"
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="نسبة الضريبة %",
    )
    attributes = models.JSONField(
        default=dict, blank=True, verbose_name="خصائص/سمات (JSON)"
    )
    slug = models.SlugField(max_length=220, blank=True, verbose_name="Slug (اختياري)")
    image = models.ImageField(
        upload_to="product_images/", blank=True, null=True, verbose_name="صورة المنتج"
    )
    qr_code = models.ImageField(
        upload_to="product_qrcodes/", blank=True, null=True, verbose_name="QR كود"
    )

    objects = ActiveQuerySet.as_manager()

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["name"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    @property
    def margin(self) -> Decimal:
        """الهامش = السعر - التكلفة (Decimal)."""
        try:
            return (self.price or Decimal("0")) - (self.cost_price or Decimal("0"))
        except Exception:
            return Decimal("0")

    @property
    def margin_percent(self) -> float:
        """نسبة الهامش كنسبة مئوية."""
        try:
            price = self.price or Decimal("0")
            if price == 0:
                return 0.0
            return float(round((self.margin / price) * 100, 2))
        except Exception:
            return 0.0

    def get_absolute_url(self) -> str:
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

    def save(self, *args, **kwargs) -> None:
        if not self.slug and self.name:
            self.slug = slugify(self.name)[:220]

        should_regen_qr = False
        if self.pk:
            try:
                prev = (
                    type(self)
                    .objects.only(
                        "name",
                        "code",
                        "uom",
                        "price",
                        "cost_price",
                        "currency",
                        "barcode",
                    )
                    .get(pk=self.pk)
                )
                fields_to_watch = [
                    "name",
                    "code",
                    "uom",
                    "price",
                    "cost_price",
                    "currency",
                    "barcode",
                ]
                should_regen_qr = any(
                    getattr(prev, f) != getattr(self, f) for f in fields_to_watch
                )
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
    product_code = models.CharField(
        max_length=100, unique=True, verbose_name="كود المنتج"
    )
    name = models.CharField(max_length=100, verbose_name="اسم المنتج")
    quantity = models.PositiveIntegerField(verbose_name="الكمية")
    date_produced = models.DateField(default=timezone.now, verbose_name="تاريخ الإنتاج")
    image = models.ImageField(
        upload_to="product_images/", blank=True, null=True, verbose_name="صورة المنتج"
    )
    quality_status = models.CharField(
        max_length=10,
        choices=QUALITY_STATUS_CHOICES,
        default="good",
        verbose_name="حالة الجودة",
    )
    expiration_date = models.DateField(
        blank=True, null=True, verbose_name="تاريخ الانتهاء (اختياري)"
    )
    qr_code = models.ImageField(
        upload_to="product_qrcodes/", blank=True, null=True, verbose_name="QR كود"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    batch_number = models.CharField(
        max_length=64, blank=True, null=True, verbose_name="رقم التشغيل/الدفعة"
    )
    lot = models.CharField(max_length=64, blank=True, null=True, verbose_name="LOT")
    location_code = models.CharField(
        max_length=64, blank=True, null=True, verbose_name="موقع التخزين (رمز)"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات داخلية")
    attributes = models.JSONField(
        default=dict, blank=True, verbose_name="خصائص/سمات (JSON)"
    )

    class Meta:
        verbose_name = "المنتج النهائي"
        verbose_name_plural = "المنتجات النهائية"
        ordering = ["-date_produced"]
        indexes = [
            models.Index(fields=["product_code"]),
            models.Index(fields=["date_produced"]),
            models.Index(fields=["quality_status"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.product_code}"

    @property
    def is_expired(self) -> bool:
        return bool(
            self.expiration_date and self.expiration_date < timezone.now().date()
        )

    def clean(self) -> None:
        if (
            self.expiration_date
            and self.date_produced
            and self.expiration_date < self.date_produced
        ):
            from django.core.exceptions import ValidationError

            raise ValidationError(
                {
                    "expiration_date": "تاريخ الانتهاء يجب أن يكون بعد/يساوي تاريخ الإنتاج."
                }
            )

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

    def save(self, *args, **kwargs) -> None:
        should_regen_qr = False
        if self.pk:
            try:
                prev = (
                    type(self)
                    .objects.only(
                        "name",
                        "product_code",
                        "quantity",
                        "date_produced",
                        "quality_status",
                        "expiration_date",
                        "batch_number",
                        "lot",
                        "location_code",
                    )
                    .get(pk=self.pk)
                )
                watch = [
                    "name",
                    "product_code",
                    "quantity",
                    "date_produced",
                    "quality_status",
                    "expiration_date",
                    "batch_number",
                    "lot",
                    "location_code",
                ]
                should_regen_qr = any(
                    getattr(prev, f) != getattr(self, f) for f in watch
                )
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
