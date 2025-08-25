from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Partner(models.Model):
    class PartnerType(models.TextChoices):
        COMPANY = 'company', _('شركة')
        PERSON  = 'person',  _('فرد')

    name = models.CharField(_("الاسم"), max_length=255)
    type = models.CharField(_("النوع"), max_length=20, choices=PartnerType.choices, default=PartnerType.PERSON)

    phone = models.CharField(_("رقم الهاتف"), max_length=30, blank=True, null=True, unique=False)
    email = models.EmailField(_("البريد الإلكتروني"), blank=True, null=True)
    tax_number = models.CharField(_("الرقم الضريبي"), max_length=64, blank=True, null=True)
    accounting_code = models.CharField(_("كود الحساب المحاسبي"), max_length=64, blank=True, null=True)

    is_active = models.BooleanField(_("نشط؟"), default=True)
    notes = models.TextField(_("ملاحظات"), blank=True, null=True)
    last_activity = models.DateTimeField(_("آخر نشاط"), default=timezone.now)

    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)

    class Meta:
        verbose_name = _("شريك")
        verbose_name_plural = _("الشركاء")
        indexes = [
            models.Index(fields=["name"], name="partners__name_idx"),
            models.Index(fields=["phone"], name="partners__phone_idx"),
            models.Index(fields=["email"], name="partners__email_idx"),
        ]

    def __str__(self):
        return self.name


class Address(models.Model):
    class AddressType(models.TextChoices):
        BILLING  = 'billing',  _('فاتورة')
        SHIPPING = 'shipping', _('شحن')
        OTHER    = 'other',    _('أخرى')

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="addresses", verbose_name=_("الشريك"))
    address_type = models.CharField(_("نوع العنوان"), max_length=20, choices=AddressType.choices, default=AddressType.BILLING)
    country = models.CharField(_("الدولة"), max_length=100, blank=True, null=True)
    governorate = models.CharField(_("المحافظة"), max_length=100, blank=True, null=True)
    city = models.CharField(_("المدينة"), max_length=100, blank=True, null=True)
    street = models.CharField(_("الشارع"), max_length=255, blank=True, null=True)
    postal_code = models.CharField(_("الرمز البريدي"), max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = _("عنوان")
        verbose_name_plural = _("العناوين")

    def __str__(self):
        return f"{self.partner.name} - {self.get_address_type_display()}"


class Customer(models.Model):
    """
    بروفايل العميل فوق Partner (OneToOne).
    """
    class ClientType(models.TextChoices):
        NEW     = 'new',     _('عميل جديد')
        REGULAR = 'regular', _('عميل منتظم')
        VIP     = 'vip',     _('عميل VIP')

    partner = models.OneToOneField(Partner, on_delete=models.CASCADE, related_name="customer_profile", verbose_name=_("الشريك"))
    client_type = models.CharField(_("نوع العميل"), max_length=10, choices=ClientType.choices, default=ClientType.NEW)
    points = models.PositiveIntegerField(_("النقاط"), default=0)
    total_purchases = models.DecimalField(_("إجمالي المشتريات"), max_digits=12, decimal_places=2, default=0)
    last_purchase_date = models.DateField(_("آخر عملية شراء"), null=True, blank=True)
    profile_image = models.ImageField(_("صورة العميل"), upload_to='clients/', blank=True, null=True)

    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)

    class Meta:
        verbose_name = _("عميل (بروفايل)")
        verbose_name_plural = _("عملاء (بروفايل)")

    def __str__(self):
        return self.partner.name

    def auto_classify(self):
        if self.total_purchases and self.total_purchases > 10000:
            return self.ClientType.VIP
        elif self.total_purchases and self.total_purchases > 2000:
            return self.ClientType.REGULAR
        return self.ClientType.NEW

    def save(self, *args, **kwargs):
        self.client_type = self.auto_classify()
        super().save(*args, **kwargs)


# Proxy لتسمية "عميل" في الأدمن واستعماله كسجل عرضي فوق Customer
class Client(Customer):
    class Meta:
        proxy = True
        verbose_name = _("عميل")
        verbose_name_plural = _("العملاء")
