# D:\ERP_CORE\accounting\models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from apps.employees.models import Employee
import json


# =========================
# الموردون والعملاء
# =========================
class Supplier(models.Model):
    """نموذج المورد."""
    name = models.CharField("اسم المورد", max_length=255, db_index=True)
    phone = models.CharField("رقم الهاتف", max_length=20, blank=True, null=True)
    email = models.EmailField("البريد الإلكتروني", blank=True, null=True)
    address = models.TextField("العنوان", blank=True, null=True)
    governorate = models.CharField("المحافظة", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "مورد"
        verbose_name_plural = "الموردين"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["phone"]),
        ]


class Customer(models.Model):
    """نموذج العميل."""
    name = models.CharField("اسم العميل", max_length=255, db_index=True)
    phone = models.CharField("رقم الهاتف", max_length=20, blank=True, null=True)
    email = models.EmailField("البريد الإلكتروني", blank=True, null=True)
    address = models.TextField("العنوان", blank=True, null=True)
    governorate = models.CharField("المحافظة", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["phone"]),
        ]


# =========================
# أوامر الدفع وطرق الدفع
# =========================
class PaymentMethod(models.Model):
    """طرق الدفع."""
    name = models.CharField("اسم طريقة الدفع", max_length=100, unique=True)
    is_active = models.BooleanField("نشطة؟", default=True)
    notes = models.TextField("ملاحظات", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "طريقة دفع"
        verbose_name_plural = "طرق الدفع"
        ordering = ["name"]


class PaymentOrder(models.Model):
    """أوامر الدفع المرتبطة بالمورد."""
    PAYMENT_METHODS = [
        ("cash", "نقدي"),
        ("bank", "تحويل بنكي"),
        ("cheque", "شيك"),
        ("other", "أخرى"),
    ]

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, verbose_name="المورد", related_name="payment_orders"
    )
    amount = models.DecimalField("المبلغ", max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    payment_method = models.CharField("طريقة الدفع", max_length=20, choices=PAYMENT_METHODS)
    payment_date = models.DateField("تاريخ الدفع", default=timezone.now)
    reference = models.CharField("مرجع", max_length=100, blank=True, null=True)
    note = models.TextField("ملاحظات", blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="أنشئ بواسطة")

    def __str__(self):
        return f"أمر دفع #{self.id} - {self.supplier.name}"

    class Meta:
        verbose_name = "أمر دفع"
        verbose_name_plural = "أوامر الدفع"
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["payment_date"]),
            models.Index(fields=["payment_method"]),
        ]


# =========================
# الأصول والاستهلاك
# =========================
class Asset(models.Model):
    """الأصول وأنواعها."""
    ASSET_TYPES = [
        ("vehicle", "مركبة"),
        ("machine", "آلة"),
        ("furniture", "أثاث"),
        ("equipment", "معدات"),
        ("other", "أخرى"),
    ]

    name = models.CharField("اسم الأصل", max_length=255)
    asset_type = models.CharField("نوع الأصل", max_length=50, choices=ASSET_TYPES, db_index=True)
    purchase_date = models.DateField("تاريخ الشراء", default=timezone.now)
    value = models.DecimalField("القيمة", max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    depreciation_rate = models.DecimalField(
        "معدل الإهلاك (%)", max_digits=5, decimal_places=2, validators=[MinValueValidator(0)],
        help_text="مثال: 10 تعني 10% سنويًا"
    )
    is_active = models.BooleanField("نشط؟", default=True)
    notes = models.TextField("ملاحظات", blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.get_asset_type_display()}"

    def annual_depreciation(self):
        return self.value * (self.depreciation_rate / 100)

    class Meta:
        verbose_name = "أصل"
        verbose_name_plural = "الأصول"
        ordering = ["-purchase_date"]
        indexes = [
            models.Index(fields=["asset_type"]),
            models.Index(fields=["is_active"]),
        ]


# =========================
# المصروفات
# =========================
class Expense(models.Model):
    """المصروفات مع التصنيفات."""
    CATEGORY_CHOICES = [
        ("rent", "إيجار"),
        ("utilities", "مرافق"),
        ("supplies", "مستلزمات"),
        ("transport", "نقل"),
        ("other", "أخرى"),
    ]

    description = models.CharField("الوصف", max_length=255)
    category = models.CharField("التصنيف", max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    amount = models.DecimalField("المبلغ", max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    date = models.DateField("التاريخ", default=timezone.now)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount} ج.م"

    class Meta:
        verbose_name = "مصروف"
        verbose_name_plural = "المصروفات"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["category"]),
        ]


# =========================
# الفواتير العامة والمدفوعات
# =========================
class Invoice(models.Model):
    """الفواتير العامة."""
    PAYMENT_METHOD_CHOICES = [
        ("cash", "نقدي"),
        ("bank", "تحويل بنكي"),
        ("vodafone", "فودافون كاش"),
        ("etisalat", "اتصالات كاش"),
        ("orange", "أورنج كاش"),
        ("instapay", "إنستا باي"),
        ("cheque", "شيك"),
    ]
    SALE_TYPE_CHOICES = [
        ("cash", "بيع نقدي"),
        ("credit", "بيع آجل"),
        ("bill_of_lading", "بوليصة شحن"),
    ]
    STATUS_CHOICES = [
        ("paid", "مدفوعة"),
        ("unpaid", "غير مدفوعة"),
        ("partial", "مدفوعة جزئيًا"),
        ("overdue", "متأخرة"),
    ]

    number = models.CharField("رقم الفاتورة", max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="invoices", verbose_name="العميل")
    date_issued = models.DateField("تاريخ الإصدار", default=timezone.now)
    due_date = models.DateField("تاريخ الاستحقاق")
    payment_method = models.CharField("طريقة الدفع", max_length=20, choices=PAYMENT_METHOD_CHOICES)
    sale_type = models.CharField("نوع البيع", max_length=20, choices=SALE_TYPE_CHOICES, default="cash")
    currency = models.CharField("العملة", max_length=10, default="EGP")
    total_amount = models.DecimalField("الإجمالي", max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default="unpaid", db_index=True)
    notes = models.TextField("ملاحظات", blank=True, null=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)

    def is_overdue(self):
        return self.status != "paid" and timezone.now().date() > self.due_date

    def __str__(self):
        return f"فاتورة {self.number} - {self.customer.name}"

    class Meta:
        verbose_name = "فاتورة"
        verbose_name_plural = "الفواتير"
        ordering = ["-date_issued"]
        indexes = [
            models.Index(fields=["date_issued"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["status"]),
        ]


class Payment(models.Model):
    """المدفوعات المرتبطة بالفواتير."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments", verbose_name="الفاتورة")
    amount = models.DecimalField("المبلغ", max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    payment_date = models.DateField("تاريخ الدفع", default=timezone.now)
    notes = models.TextField("ملاحظات", blank=True, null=True)

    def __str__(self):
        return f"دفع {self.amount} لفاتورة {self.invoice.number}"

    class Meta:
        verbose_name = "سداد فاتورة"
        verbose_name_plural = "سداد الفواتير"
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["payment_date"]),
        ]


# =========================
# القيود المحاسبية
# =========================
class Account(models.Model):
    """الحسابات المالية."""
    ACCOUNT_TYPES = [
        ("asset", "أصل"),
        ("liability", "التزام"),
        ("equity", "حقوق ملكية"),
        ("income", "إيراد"),
        ("expense", "مصروف"),
    ]

    name = models.CharField("اسم الحساب", max_length=255)
    code = models.CharField("كود الحساب", max_length=20, unique=True, db_index=True)
    type = models.CharField("نوع الحساب", max_length=50, choices=ACCOUNT_TYPES, db_index=True)
    supplier = models.OneToOneField(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="account", verbose_name="يرتبط بمورد"
    )
    customer = models.OneToOneField(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="account", verbose_name="يرتبط بعميل"
    )

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "حساب"
        verbose_name_plural = "الحسابات"
        ordering = ["code"]


class JournalEntry(models.Model):
    """قيود اليومية."""
    ENTRY_TYPE_CHOICES = [
        ("manual", "يدوي"),
        ("system", "آلي"),
    ]

    date = models.DateField("التاريخ", default=timezone.now)
    description = models.CharField("الوصف", max_length=255)
    amount = models.DecimalField("الإجمالي", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    entry_type = models.CharField("نوع القيد", max_length=20, choices=ENTRY_TYPE_CHOICES, default="manual", db_index=True)
    debit = models.DecimalField("مدين", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    credit = models.DecimalField("دائن", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    invoice = models.ForeignKey(
        Invoice, on_delete=models.SET_NULL, blank=True, null=True, related_name="journal_entries", verbose_name="فاتورة مرتبطة"
    )
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="أنشئ بواسطة")

    def __str__(self):
        return f"{self.date} - {self.description}"

    class Meta:
        verbose_name = "قيد يومية"
        verbose_name_plural = "قيود اليومية"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["entry_type"]),
        ]


class JournalItem(models.Model):
    """بنود قيود اليومية."""
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="items", verbose_name="القيد")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name="الحساب")
    debit = models.DecimalField("مدين", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    credit = models.DecimalField("دائن", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.account.name} - مدين: {self.debit} / دائن: {self.credit}"

    class Meta:
        verbose_name = "بند قيد"
        verbose_name_plural = "بنود القيود"


# =========================
# اقتراحات الذكاء المحاسبية
# =========================
class AccountingSuggestionLog(models.Model):
    """سجل اقتراحات الذكاء الاصطناعي للمحاسبة."""
    timestamp = models.DateTimeField("الزمن", auto_now_add=True)
    suggested_by_ai = models.BooleanField("مُقترح بواسطة الذكاء الاصطناعي؟", default=True)
    suggestion_type = models.CharField("نوع الاقتراح", max_length=100, db_index=True)
    description = models.TextField("الوصف")
    risk_level = models.CharField(
        "مستوى الخطورة", max_length=20,
        choices=[("Low", "منخفض"), ("Medium", "متوسط"), ("High", "مرتفع")],
        db_index=True
    )
    resolved = models.BooleanField("تمت المعالجة؟", default=False)

    def __str__(self):
        return f"{self.suggestion_type} - {self.risk_level}"

    class Meta:
        verbose_name = "سجل اقتراح محاسبي"
        verbose_name_plural = "سجل اقتراحات محاسبية"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["risk_level"]),
            models.Index(fields=["resolved"]),
        ]


# =========================
# التصنيع: BOM + أوامر تصنيع
# =========================
class BillOfMaterial(models.Model):
    """قائمة مواد التصنيع (BOM)."""
    name = models.CharField("اسم الـBOM", max_length=255)
    product_name = models.CharField("اسم المنتج", max_length=255, db_index=True)
    components_json = models.TextField("المكوّنات (JSON)", blank=True, null=True)
    total_cost = models.DecimalField("إجمالي التكلفة", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    @property
    def components(self):
        if self.components_json:
            try:
                return json.loads(self.components_json)
            except Exception:
                return {}
        return {}

    @components.setter
    def components(self, value):
        self.components_json = json.dumps(value or {}, ensure_ascii=False)

    def __str__(self):
        return f"{self.name} - {self.product_name}"

    class Meta:
        verbose_name = "قائمة مواد (BOM)"
        verbose_name_plural = "قوائم المواد (BOM)"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["product_name"]),
        ]


class ManufacturingOrder(models.Model):
    """أوامر التصنيع."""
    STATUS_CHOICES = [
        ("pending", "قيد الانتظار"),
        ("in_progress", "جارٍ التصنيع"),
        ("completed", "تم التصنيع"),
    ]

    order_number = models.CharField("رقم أمر التصنيع", max_length=50, unique=True, db_index=True)
    bom = models.ForeignKey(BillOfMaterial, on_delete=models.CASCADE, related_name="manufacturing_orders", verbose_name="قائمة المواد")
    quantity = models.PositiveIntegerField("الكمية", default=1, validators=[MinValueValidator(1)])
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    start_date = models.DateField("تاريخ البدء", default=timezone.now)
    end_date = models.DateField("تاريخ الانتهاء", blank=True, null=True)
    actual_cost = models.DecimalField("التكلفة الفعلية", max_digits=12, decimal_places=2, blank=True, null=True)
    notes = models.TextField("ملاحظات", blank=True, null=True)

    def __str__(self):
        return f"أمر تصنيع {self.order_number} - {self.bom.product_name}"

    class Meta:
        verbose_name = "أمر تصنيع"
        verbose_name_plural = "أوامر التصنيع"
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["start_date"]),
        ]


# =========================
# فواتير الموردين/المبيعات/المشتريات + البنود
# =========================
class SupplierInvoice(models.Model):
    """فواتير الموردين."""
    PAYMENT_METHOD_CHOICES = [
        ("cash", "نقدي"),
        ("bank", "تحويل بنكي"),
        ("cheque", "شيك"),
        ("vodafone", "فودافون كاش"),
        ("etisalat", "اتصالات كاش"),
        ("orange", "أورنج كاش"),
        ("instapay", "إنستا باي"),
    ]
    STATUS_CHOICES = [
        ("unpaid", "غير مدفوعة"),
        ("partial", "مدفوعة جزئيًا"),
        ("paid", "مدفوعة"),
        ("overdue", "متأخرة"),
    ]

    number = models.CharField("رقم الفاتورة", max_length=50, unique=True, db_index=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="supplier_invoices", verbose_name="المورد")
    date_issued = models.DateField("تاريخ الإصدار", default=timezone.now)
    due_date = models.DateField("تاريخ الاستحقاق")
    payment_method = models.CharField("طريقة الدفع", max_length=20, choices=PAYMENT_METHOD_CHOICES)
    currency = models.CharField("العملة", max_length=10, default="EGP")
    total_amount = models.DecimalField("الإجمالي", max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default="unpaid", db_index=True)
    notes = models.TextField("ملاحظات", blank=True, null=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)

    def is_overdue(self):
        return self.status != "paid" and timezone.now().date() > self.due_date

    def __str__(self):
        return f"فاتورة مورد {self.number} - {self.supplier.name}"

    class Meta:
        verbose_name = "فاتورة مورد"
        verbose_name_plural = "فواتير الموردين"
        ordering = ["-date_issued"]
        indexes = [
            models.Index(fields=["date_issued"]),
            models.Index(fields=["status"]),
        ]


class SalesInvoice(models.Model):
    """فواتير المبيعات."""
    number = models.CharField("رقم الفاتورة", max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="sales_invoices", verbose_name="العميل")
    date_issued = models.DateField("تاريخ الإصدار", default=timezone.now)
    due_date = models.DateField("تاريخ الاستحقاق")
    total_amount = models.DecimalField("الإجمالي", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    status = models.CharField(
        "الحالة", max_length=20,
        choices=[("unpaid", "غير مدفوعة"), ("partial", "مدفوعة جزئيًا"), ("paid", "مدفوعة"), ("overdue", "متأخرة")],
        default="unpaid", db_index=True
    )
    notes = models.TextField("ملاحظات", blank=True, null=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="أنشئ بواسطة")
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)

    def __str__(self):
        return f"فاتورة مبيعات {self.number}"

    class Meta:
        verbose_name = "فاتورة مبيعات"
        verbose_name_plural = "فواتير المبيعات"
        ordering = ["-date_issued"]
        indexes = [
            models.Index(fields=["date_issued"]),
            models.Index(fields=["status"]),
        ]


class PurchaseInvoice(models.Model):
    """فواتير المشتريات."""
    number = models.CharField("رقم الفاتورة", max_length=50, unique=True, db_index=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="purchase_invoices", verbose_name="المورد")
    date_issued = models.DateField("تاريخ الشراء", default=timezone.now)
    due_date = models.DateField("تاريخ الاستحقاق")
    total_amount = models.DecimalField("الإجمالي", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    status = models.CharField(
        "الحالة", max_length=20,
        choices=[("unpaid", "غير مدفوعة"), ("partial", "مدفوعة جزئيًا"), ("paid", "مدفوعة"), ("overdue", "متأخرة")],
        default="unpaid", db_index=True
    )
    notes = models.TextField("ملاحظات", blank=True, null=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="أنشئ بواسطة")
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)

    def __str__(self):
        return f"فاتورة مشتريات {self.number}"

    class Meta:
        verbose_name = "فاتورة مشتريات"
        verbose_name_plural = "فواتير المشتريات"
        ordering = ["-date_issued"]
        indexes = [
            models.Index(fields=["date_issued"]),
            models.Index(fields=["status"]),
        ]


class InvoiceItem(models.Model):
    """بنود الفواتير (بيع وشراء)."""
    sales_invoice = models.ForeignKey(
        SalesInvoice, on_delete=models.CASCADE, null=True, blank=True, related_name="items", verbose_name="فاتورة مبيعات"
    )
    purchase_invoice = models.ForeignKey(
        PurchaseInvoice, on_delete=models.CASCADE, null=True, blank=True, related_name="items", verbose_name="فاتورة مشتريات"
    )
    product_name = models.CharField("اسم المنتج", max_length=255)
    quantity = models.PositiveIntegerField("الكمية", validators=[MinValueValidator(1)])
    unit_price = models.DecimalField("سعر الوحدة", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    notes = models.TextField("ملاحظات", blank=True, null=True)

    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    class Meta:
        verbose_name = "بند فاتورة"
        verbose_name_plural = "بنود الفواتير"


# =========================
# العمليات النقدية
# =========================
class CashTransaction(models.Model):
    """سجل العمليات النقدية."""
    amount = models.DecimalField("المبلغ", max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    date = models.DateField("التاريخ", default=timezone.now)
    description = models.TextField("الوصف", blank=True, null=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)

    def __str__(self):
        return f"{self.amount} - {self.date}"

    class Meta:
        verbose_name = "عملية نقدية"
        verbose_name_plural = "عمليات نقدية"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date"]),
        ]
