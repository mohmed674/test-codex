# apps/accounting/tasks.py
from contextlib import suppress

from celery import shared_task
from django.apps import apps
from django.db import connection
from django.db.models import Q
from django.utils import timezone

from .models import Invoice, JournalEntry, ManufacturingOrder, SupplierInvoice


def _get_model_if_ready(app_label: str, model_name: str):
    """رجّع الموديل فقط لو جدولُه موجود لتفادي أعطال المهام."""
    with suppress(Exception):
        model = apps.get_model(app_label, model_name)
        table = model._meta.db_table  # type: ignore[attr-defined]
        if table in connection.introspection.table_names():
            return model
    return None


def _create_alert(section: str, alert_type: str, level: str, message: str) -> None:
    """إنشاء AIDecisionAlert بأمان إن وُجد الموديل والجدول."""
    AIDecisionAlert = _get_model_if_ready("ai_decision", "AIDecisionAlert")
    if AIDecisionAlert is None:
        return
    with suppress(Exception):
        AIDecisionAlert.objects.get_or_create(  # type: ignore[call-arg]
            section=section,
            alert_type=alert_type,
            level=level,
            message=message,
        )


def _create_risk_incident(category: str, event_type: str, risk_level: str, notes: str):
    """إنشاء RiskIncident بأمان إن وُجد الموديل والجدول."""
    RiskIncident = _get_model_if_ready("internal_monitoring", "RiskIncident")
    if RiskIncident is None:
        return
    with suppress(Exception):
        RiskIncident.objects.create(  # type: ignore[call-arg]
            category=category,
            event_type=event_type,
            risk_level=risk_level,
            notes=notes,
        )


@shared_task
def detect_high_value_entries_task(threshold: float = 50_000) -> None:
    """
    ✅ مهمة دورية لرصد القيود ذات القيمة العالية.
    يعتبر القيد مرتفعًا لو أي من (debit/credit) ≥ threshold.
    """
    entries = JournalEntry.objects.filter(
        Q(debit__gte=threshold) | Q(credit__gte=threshold)
    )
    for entry in entries:
        amount = entry.debit or entry.credit
        _create_alert(
            section="accounting",
            alert_type="قيد مرتفع",
            level="high",
            message=("⚠️ قيد محاسبي مرتفع: " f"{entry.description} - {amount}"),
        )


@shared_task
def detect_overdue_supplier_payments_task() -> None:
    """
    ✅ تنبيه الموردين المتأخرين في السداد (فواتير الموردين غير المسددة).
    """
    today = timezone.now().date()
    overdue_invoices = SupplierInvoice.objects.filter(
        status__in=["unpaid", "partial"],
        due_date__lt=today,
    )

    for invoice in overdue_invoices:
        _create_alert(
            section="accounting",
            alert_type="تأخير دفع للمورد",
            level="medium",
            message=(
                "📌 تأخير في سداد فاتورة "
                f"{invoice.number} للمورد {invoice.supplier.name}"
            ),
        )
        _create_risk_incident(
            category="Finance",
            event_type="تأخير سداد فاتورة مورد",
            risk_level="Medium",
            notes=(
                f"فاتورة: {invoice.number} / المورد: {invoice.supplier.name} / "
                f"التاريخ: {invoice.due_date}"
            ),
        )


@shared_task
def detect_overdue_customer_invoices_task() -> None:
    """
    ✅ تنبيه العملاء المتأخرين عن السداد.
    """
    today = timezone.now().date()
    overdue_invoices = Invoice.objects.filter(
        status__in=["unpaid", "partial"],
        due_date__lt=today,
    )

    for invoice in overdue_invoices:
        _create_alert(
            section="accounting",
            alert_type="فاتورة متأخرة",
            level="high",
            message=(
                "📌 تأخير في سداد فاتورة "
                f"{invoice.number} للعميل {invoice.customer.name}"
            ),
        )
    _log_overdue_customer_incidents(overdue_invoices)


def _log_overdue_customer_incidents(overdue_invoices) -> None:
    """تفريغ إنشاء سجلات المخاطر لأسطر أقصر وأوضح."""
    for invoice in overdue_invoices:
        _create_risk_incident(
            category="Finance",
            event_type="تأخير سداد فاتورة عميل",
            risk_level="High",
            notes=(
                f"فاتورة: {invoice.number} / العميل: {invoice.customer.name} / "
                f"التاريخ: {invoice.due_date}"
            ),
        )


@shared_task
def detect_unrecorded_manufacturing_orders_task() -> None:
    """
    ✅ رصد أوامر التصنيع المكتملة التي لم تُسجل كمحاسبة.
    ملاحظة: يعتمد على وجود علاقة يومية مع أمر التصنيع إن كانت معرفة بالمشروع.
    """
    done_orders = ManufacturingOrder.objects.filter(
        status="completed",
        journalentry__isnull=True,  # تُستخدم إذا كان هناك علاقة معرفة في المشروع
    )

    for order in done_orders:
        product_name = getattr(getattr(order, "bom", None), "product_name", "")
        _create_alert(
            section="accounting",
            alert_type="أمر تصنيع غير مقيد",
            level="medium",
            message=("🛠️ أمر تصنيع مكتمل لم يُسجَّل في المحاسبة: " f"{product_name}"),
        )
        _create_risk_incident(
            category="Manufacturing",
            event_type="عدم تسجيل أمر تصنيع",
            risk_level="Medium",
            notes=(f"اسم المنتج: {product_name} / رقم الأمر: {order.pk}"),
        )
