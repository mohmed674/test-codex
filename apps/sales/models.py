from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.products.models import FinishedProduct  # ← تم التعديل هنا فقط
from apps.employees.models import Employee
from apps.clients.models import Client

# ✅ سجل الفواتير
class SaleInvoice(models.Model):
    PAYMENT_METHODS = [
        ('cash', _('نقدي')),
        ('vodafone_cash', _('فودافون كاش')),
        ('instapay', _('إنستاباي')),
        ('bank', _('تحويل بنكي')),
        ('cheque', _('شيك')),
        ('card', _('بطاقة ائتمان')),
        ('valu', _('ValU')),
        ('paypal', _('PayPal')),
        ('postpaid', _('دفع لاحق')),
    ]

    invoice_number = models.CharField(_("رقم الفاتورة"), max_length=20, unique=True)
    client = models.ForeignKey(Client, verbose_name=_("العميل"), on_delete=models.CASCADE)
    date = models.DateField(_("تاريخ الفاتورة"), default=timezone.now)
    total_amount = models.DecimalField(_("إجمالي المبلغ"), max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(_("طريقة الدفع"), max_length=30, choices=PAYMENT_METHODS)
    created_by = models.ForeignKey(Employee, verbose_name=_("أنشأ بواسطة"), on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)

    accounting_code = models.CharField(_("كود الحساب المحاسبي"), max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = _("فاتورة بيع")
        verbose_name_plural = _("فواتير البيع")

    def __str__(self):
        return f"فاتورة {self.invoice_number} - {self.client.name}"

    def calculate_total(self):
        total = sum([item.total for item in self.items.all()])
        self.total_amount = total
        self.save(update_fields=['total_amount'])
        return total

    def add_client_points(self):
        points = int(self.total_amount // 100)
        if points > 0:
            self.client.points += points
            self.client.save()
            ClientPointsLog.objects.create(client=self.client, points=points, source_invoice=self)


# ✅ بنود الفاتورة
class SaleItem(models.Model):
    invoice = models.ForeignKey(SaleInvoice, related_name='items', verbose_name=_("الفاتورة"), on_delete=models.CASCADE)
    product = models.ForeignKey(FinishedProduct, verbose_name=_("المنتج"), on_delete=models.CASCADE)  # ← هنا فقط
    quantity = models.PositiveIntegerField(_("الكمية"))
    unit_price = models.DecimalField(_("سعر الوحدة"), max_digits=8, decimal_places=2)
    discount = models.DecimalField(_("الخصم"), max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("بند فاتورة")
        verbose_name_plural = _("بنود الفاتورة")

    @property
    def total(self):
        return (self.unit_price * self.quantity) - self.discount

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"


# ✅ سجل نقاط العملاء
class ClientPointsLog(models.Model):
    client = models.ForeignKey(Client, verbose_name=_("العميل"), on_delete=models.CASCADE)
    points = models.PositiveIntegerField(_("النقاط"))
    source_invoice = models.ForeignKey(SaleInvoice, verbose_name=_("مصدر النقاط"), on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(_("تاريخ الإضافة"), auto_now_add=True)

    class Meta:
        verbose_name = _("سجل نقاط العميل")
        verbose_name_plural = _("سجلات نقاط العملاء")

    def __str__(self):
        return f"{self.client.name} +{self.points} نقطة"


# ✅ أداء مندوبي المبيعات
class SalesPerformance(models.Model):
    employee = models.ForeignKey(Employee, verbose_name=_("الموظف"), on_delete=models.CASCADE)
    date = models.DateField(_("التاريخ"))
    sales_total = models.DecimalField(_("إجمالي المبيعات"), max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('employee', 'date')
        verbose_name = _("أداء مبيعات")
        verbose_name_plural = _("أداء المبيعات")

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.sales_total}"


# ✅ تحليل مبيعات المنتجات
class ProductSalesAnalysis(models.Model):
    product = models.ForeignKey(FinishedProduct, verbose_name=_("المنتج"), on_delete=models.CASCADE)  # ← هنا فقط
    month = models.DateField(_("الشهر"))
    total_sold = models.PositiveIntegerField(_("إجمالي المبيعات"), default=0)
    alerts = models.TextField(_("تنبيهات"), blank=True, null=True)

    class Meta:
        verbose_name = _("تحليل مبيعات المنتج")
        verbose_name_plural = _("تحليلات مبيعات المنتجات")

    def __str__(self):
        return f"تحليل {self.product.name} - {self.month}"


# ✅ تحليل نشاط العميل
class ClientActivity(models.Model):
    client = models.ForeignKey(Client, verbose_name=_("العميل"), on_delete=models.CASCADE)
    last_purchase_date = models.DateField(_("آخر شراء"), null=True, blank=True)
    total_purchases = models.DecimalField(_("إجمالي الشراء"), max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(_("نشط؟"), default=True)

    class Meta:
        verbose_name = _("نشاط العميل")
        verbose_name_plural = _("تحليل نشاط العملاء")

    def __str__(self):
        return f"نشاط {self.client.name}"


# ✅ اقتراحات ذكية من AI
class SmartSalesSuggestion(models.Model):
    product = models.ForeignKey(FinishedProduct, verbose_name=_("المنتج"), on_delete=models.CASCADE)  # ← هنا فقط
    suggested_action = models.TextField(_("الاقتراح"))
    created_at = models.DateTimeField(_("تاريخ الاقتراح"), auto_now_add=True)

    class Meta:
        verbose_name = _("اقتراح مبيعات ذكي")
        verbose_name_plural = _("اقتراحات المبيعات الذكية")

    def __str__(self):
        return f"اقتراح لـ {self.product.name}"
