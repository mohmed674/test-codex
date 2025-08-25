# apps/banking/models.py — Week 1 (Banking Integration Layer) — Final & Extensible

from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Currency(models.TextChoices):
    EGP = "EGP", _("Egyptian Pound")
    USD = "USD", _("US Dollar")
    EUR = "EUR", _("Euro")
    SAR = "SAR", _("Saudi Riyal")
    AED = "AED", _("UAE Dirham")


class PaymentDirection(models.TextChoices):
    IN = "in", _("Incoming")
    OUT = "out", _("Outgoing")


class PaymentMethod(models.TextChoices):
    CARD = "card", _("Card")
    BANK_TRANSFER = "bank_transfer", _("Bank Transfer")
    WALLET = "wallet", _("Wallet")
    CASH = "cash", _("Cash")


class PaymentStatus(models.TextChoices):
    INITIATED = "initiated", _("Initiated")
    PENDING = "pending", _("Pending")
    SUCCEEDED = "succeeded", _("Succeeded")
    FAILED = "failed", _("Failed")
    REFUNDED = "refunded", _("Refunded")
    CANCELLED = "cancelled", _("Cancelled")


class TransferStatus(models.TextChoices):
    CREATED = "created", _("Created")
    SCHEDULED = "scheduled", _("Scheduled")
    PROCESSING = "processing", _("Processing")
    COMPLETED = "completed", _("Completed")
    FAILED = "failed", _("Failed")


class TransactionType(models.TextChoices):
    CREDIT = "credit", _("Credit")
    DEBIT = "debit", _("Debit")


class ReconciliationStatus(models.TextChoices):
    OPEN = "open", _("Open")
    MATCHED = "matched", _("Matched")
    PARTIAL = "partial", _("Partial")
    CLOSED = "closed", _("Closed")


class WebhookStatus(models.TextChoices):
    RECEIVED = "received", _("Received")
    PROCESSED = "processed", _("Processed")
    FAILED = "failed", _("Failed")


class BankProvider(models.Model):
    """
    تعريف مزوّد الخدمة البنكية (بوابة دفع/بنك).
    إعدادات حساسة تُخزَّن عادة في البيئة/الخزنة وتُحقن وقت التشغيل،
    وهذا السجل لتوصيف المزوّد وتعريف قواعد الدمج.
    """
    name = models.CharField(max_length=120, verbose_name=_("اسم المزوّد"))
    code = models.SlugField(max_length=50, unique=True, verbose_name=_("الكود"))
    base_url = models.URLField(blank=True, null=True, verbose_name=_("الرابط الأساسي"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    config = models.JSONField(default=dict, blank=True, verbose_name=_("إعدادات إضافية"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))

    class Meta:
        verbose_name = _("مزود بنكي")
        verbose_name_plural = _("مزودون بنكيون")
        indexes = [
            models.Index(fields=["code"], name="ix_banking_provider_code"),
            models.Index(fields=["is_active"], name="ix_banking_provider_active"),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class BankAccount(models.Model):
    """
    حساب بنكي أو محفظة تابعة لمزوّد.
    """
    provider = models.ForeignKey(BankProvider, on_delete=models.PROTECT, related_name="accounts", verbose_name=_("المزوّد"))
    name = models.CharField(max_length=120, verbose_name=_("اسم الحساب"))
    account_number = models.CharField(max_length=64, verbose_name=_("رقم الحساب/IBAN"))
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.EGP, verbose_name=_("العملة"))
    external_id = models.CharField(max_length=120, blank=True, null=True, verbose_name=_("المعرف الخارجي"))
    is_default = models.BooleanField(default=False, verbose_name=_("افتراضي"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))

    class Meta:
        verbose_name = _("حساب بنكي")
        verbose_name_plural = _("حسابات بنكية")
        unique_together = [("provider", "account_number")]
        indexes = [
            models.Index(fields=["provider", "account_number"], name="ix_banking_acc_provider_accno"),
            models.Index(fields=["currency"], name="ix_banking_acc_currency"),
            models.Index(fields=["is_default"], name="ix_banking_acc_default"),
        ]

    def __str__(self):
        return f"{self.name} — {self.account_number} [{self.currency}]"


class Payment(models.Model):
    """
    سجل عملية دفع/تحصيل عبر مزوّد.
    """
    provider = models.ForeignKey(BankProvider, on_delete=models.PROTECT, related_name="payments", verbose_name=_("المزوّد"))
    account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="payments", verbose_name=_("الحساب"))
    direction = models.CharField(max_length=3, choices=PaymentDirection.choices, verbose_name=_("الاتجاه"))
    method = models.CharField(max_length=20, choices=PaymentMethod.choices, verbose_name=_("الطريقة"))
    status = models.CharField(max_length=12, choices=PaymentStatus.choices, default=PaymentStatus.INITIATED, verbose_name=_("الحالة"))
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_("المبلغ"))
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.EGP, verbose_name=_("العملة"))
    reference = models.CharField(max_length=120, unique=True, verbose_name=_("مرجع العملية"))
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("الوصف"))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("بيانات إضافية"))
    external_id = models.CharField(max_length=120, blank=True, null=True, verbose_name=_("المعرف الخارجي"))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("أنشأها"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))

    class Meta:
        verbose_name = _("دفع")
        verbose_name_plural = _("دفعات")
        indexes = [
            models.Index(fields=["reference"], name="ix_banking_payment_ref"),
            models.Index(fields=["status"], name="ix_banking_payment_status"),
            models.Index(fields=["created_at"], name="ix_banking_payment_created"),
        ]

    def __str__(self):
        return f"{self.reference} — {self.amount} {self.currency} ({self.get_status_display()})"


class Transfer(models.Model):
    """
    تحويل بين حسابين (داخلي/خارجي).
    """
    provider = models.ForeignKey(BankProvider, on_delete=models.PROTECT, related_name="transfers", verbose_name=_("المزوّد"))
    source_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="outgoing_transfers", verbose_name=_("من حساب"))
    destination_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="incoming_transfers", verbose_name=_("إلى حساب"))
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_("المبلغ"))
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.EGP, verbose_name=_("العملة"))
    status = models.CharField(max_length=12, choices=TransferStatus.choices, default=TransferStatus.CREATED, verbose_name=_("الحالة"))
    scheduled_at = models.DateTimeField(blank=True, null=True, verbose_name=_("موعد مجدول"))
    executed_at = models.DateTimeField(blank=True, null=True, verbose_name=_("تاريخ التنفيذ"))
    reference = models.CharField(max_length=120, unique=True, verbose_name=_("مرجع التحويل"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("أنشأها"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))

    class Meta:
        verbose_name = _("تحويل")
        verbose_name_plural = _("تحويلات")
        indexes = [
            models.Index(fields=["reference"], name="ix_banking_transfer_ref"),
            models.Index(fields=["status"], name="ix_banking_transfer_status"),
        ]

    def __str__(self):
        return f"Transfer {self.reference} — {self.amount} {self.currency} ({self.get_status_display()})"


class BankTransaction(models.Model):
    """
    حركة كشف حساب (بيان بنكي).
    """
    account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="transactions", verbose_name=_("الحساب"))
    type = models.CharField(max_length=6, choices=TransactionType.choices, verbose_name=_("النوع"))
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_("المبلغ"))
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.EGP, verbose_name=_("العملة"))
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("الوصف"))
    external_id = models.CharField(max_length=120, blank=True, null=True, verbose_name=_("المعرف الخارجي"))
    value_date = models.DateTimeField(default=timezone.now, verbose_name=_("تاريخ القيمة"))
    booked_at = models.DateTimeField(default=timezone.now, verbose_name=_("تاريخ القيد"))
    balance_after = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0.00"), verbose_name=_("الرصيد بعد العملية"))
    raw = models.JSONField(default=dict, blank=True, verbose_name=_("البيان الخام"))

    class Meta:
        verbose_name = _("معاملة بنكية")
        verbose_name_plural = _("معاملات بنكية")
        indexes = [
            models.Index(fields=["account", "booked_at"], name="ix_banking_txn_booked"),
            models.Index(fields=["external_id"], name="ix_banking_txn_external"),
        ]

    def __str__(self):
        sign = "+" if self.type == TransactionType.CREDIT else "-"
        return f"{sign}{self.amount} {self.currency} — {self.account.name}"


class ReconciliationBatch(models.Model):
    """
    دفعة مطابقة بنكية للفترة الزمنية المحددة.
    """
    provider = models.ForeignKey(BankProvider, on_delete=models.PROTECT, related_name="reconciliations", verbose_name=_("المزوّد"))
    account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="reconciliations", verbose_name=_("الحساب"))
    period_start = models.DateTimeField(verbose_name=_("بداية الفترة"))
    period_end = models.DateTimeField(verbose_name=_("نهاية الفترة"))
    status = models.CharField(max_length=8, choices=ReconciliationStatus.choices, default=ReconciliationStatus.OPEN, verbose_name=_("الحالة"))
    matched_count = models.PositiveIntegerField(default=0, verbose_name=_("عدد المطابق"))
    unmatched_count = models.PositiveIntegerField(default=0, verbose_name=_("غير مطابق"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("أنشأها"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))

    class Meta:
        verbose_name = _("دفعة مطابقة")
        verbose_name_plural = _("دفعات مطابقة")
        indexes = [
            models.Index(fields=["status"], name="ix_banking_recon_status"),
            models.Index(fields=["period_start", "period_end"], name="ix_banking_recon_period"),
        ]

    def __str__(self):
        return f"Recon {self.account.name} [{self.period_start.date()} → {self.period_end.date()}] ({self.get_status_display()})"


class WebhookEvent(models.Model):
    """
    استقبال أحداث Webhook من المزوّدين ومعالجتها.
    """
    provider = models.ForeignKey(BankProvider, on_delete=models.PROTECT, related_name="webhooks", verbose_name=_("المزوّد"))
    event_type = models.CharField(max_length=120, verbose_name=_("نوع الحدث"))
    signature = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("التوقيع"))
    payload = models.JSONField(verbose_name=_("البيانات"))
    received_at = models.DateTimeField(auto_now_add=True, verbose_name=_("وقت الاستلام"))
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name=_("وقت المعالجة"))
    status = models.CharField(max_length=10, choices=WebhookStatus.choices, default=WebhookStatus.RECEIVED, verbose_name=_("الحالة"))
    error_message = models.TextField(blank=True, null=True, verbose_name=_("خطأ"))

    class Meta:
        verbose_name = _("حدث Webhook")
        verbose_name_plural = _("أحداث Webhook")
        indexes = [
            models.Index(fields=["provider", "event_type"], name="ix_banking_webhook_event"),
            models.Index(fields=["status"], name="ix_banking_webhook_status"),
            models.Index(fields=["received_at"], name="ix_banking_webhook_received"),
        ]

    def __str__(self):
        return f"{self.provider.code}:{self.event_type} [{self.get_status_display()}]"
