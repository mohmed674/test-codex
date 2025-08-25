from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import JournalEntry, Invoice, Supplier, ManufacturingOrder, SupplierInvoice
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident


@shared_task
def detect_high_value_entries_task(threshold=50000):
    """
    ✅ مهمة دورية لرصد القيود ذات القيمة العالية.
    """
    entries = JournalEntry.objects.filter(debit__gte=threshold) | JournalEntry.objects.filter(credit__gte=threshold)
    for entry in entries:
        AIDecisionAlert.objects.get_or_create(
            section='accounting',
            alert_type='قيد مرتفع',
            level='high',
            message=f"⚠️ قيد محاسبي مرتفع: {entry.description} - {entry.debit or entry.credit}"
        )


@shared_task
def detect_overdue_supplier_payments_task():
    """
    ✅ تنبيه الموردين المتأخرين في السداد (فواتير الموردين غير المسددة).
    """
    today = timezone.now().date()
    overdue_invoices = SupplierInvoice.objects.filter(status__in=['unpaid', 'partial'], due_date__lt=today)

    for invoice in overdue_invoices:
        AIDecisionAlert.objects.get_or_create(
            section='accounting',
            alert_type='تأخير دفع للمورد',
            level='medium',
            message=f"📌 تأخير في سداد فاتورة {invoice.number} للمورد {invoice.supplier.name}"
        )

        RiskIncident.objects.create(
            category='Finance',
            event_type='تأخير سداد فاتورة مورد',
            risk_level='Medium',
            notes=f"فاتورة: {invoice.number} / المورد: {invoice.supplier.name} / التاريخ: {invoice.due_date}"
        )


@shared_task
def detect_overdue_customer_invoices_task():
    """
    ✅ تنبيه العملاء المتأخرين عن السداد.
    """
    today = timezone.now().date()
    overdue_invoices = Invoice.objects.filter(status__in=['unpaid', 'partial'], due_date__lt=today)

    for invoice in overdue_invoices:
        AIDecisionAlert.objects.get_or_create(
            section='accounting',
            alert_type='فاتورة متأخرة',
            level='high',
            message=f"📌 تأخير في سداد فاتورة {invoice.number} للعميل {invoice.customer.name}"
        )

        RiskIncident.objects.create(
            category='Finance',
            event_type='تأخير سداد فاتورة عميل',
            risk_level='High',
            notes=f"فاتورة: {invoice.number} / العميل: {invoice.customer.name} / التاريخ: {invoice.due_date}"
        )


@shared_task
def detect_unrecorded_manufacturing_orders_task():
    """
    ✅ رصد أوامر التصنيع المكتملة التي لم تُسجل كمحاسبة.
    """
    done_orders = ManufacturingOrder.objects.filter(status='completed', journalentry__isnull=True)

    for order in done_orders:
        AIDecisionAlert.objects.get_or_create(
            section='accounting',
            alert_type='أمر تصنيع غير مقيد',
            level='medium',
            message=f"🛠️ أمر تصنيع مكتمل لم يُسجل في المحاسبة: {order.bom.product_name}"
        )

        RiskIncident.objects.create(
            category='Manufacturing',
            event_type='عدم تسجيل أمر تصنيع',
            risk_level='Medium',
            notes=f"اسم المنتج: {order.bom.product_name} / رقم الأمر: {order.id}"
        )
