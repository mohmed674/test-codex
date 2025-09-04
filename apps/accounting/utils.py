"""
Utilities for the Accounting app –
مستوى احترافي يوازي أنظمة مثل Odoo/SAP.
تحتوي هذه الوحدة على أدوات خدمية تدعم التعاملات المحاسبية مثل
الترقيم، التوليد، والتحويلات.
"""

from __future__ import annotations

from datetime import date as _date
from datetime import datetime as _datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable, Optional, Tuple, Type

from django.db import models, transaction
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from weasyprint import HTML

from .models import Account, Invoice, JournalEntry, JournalItem

__all__ = [
    "generate_sequence",
    "parse_decimal",
    "compute_invoice_total",
    "post_journal_entry",
    "safe_status_display",
    "pdf_from_template",
]


# =========================
# ثابت للقيم الرقمية الافتراضية (معالجة B008)
# =========================
_DEFAULT_DECIMAL: Decimal = Decimal("0")


# =========================
# الترقيم التلقائي
# =========================
def generate_sequence(
    model_cls: Type[models.Model],
    field_name: str = "number",
    prefix: str = "SEQ",
    when: Optional[_datetime] = None,
) -> str:
    """
    توليد رقم متسلسل بالشكل: {PREFIX}-YYYYMM-0001
    يعمل لأي موديل يحتوي على حقل رقم أو كود (مثل الفواتير، السندات، إلخ).
    """
    when = when or timezone.now()
    yyyymm = when.strftime("%Y%m")
    base = f"{prefix}-{yyyymm}-"

    qs = model_cls.objects.filter(**{f"{field_name}__startswith": base})
    last = qs.order_by(f"-{field_name}").values_list(field_name, flat=True).first()

    if not last:
        seq = 1
    else:
        try:
            seq = int(str(last).split("-")[-1]) + 1
        except Exception:
            seq = 1

    return f"{base}{seq:04d}"


# =========================
# تحويل القيم الرقمية
# =========================
def parse_decimal(value: Any, default: Decimal = _DEFAULT_DECIMAL) -> Decimal:
    """
    تحويل آمن لأي قيمة إلى Decimal، بما يتوافق مع التعاملات المالية.
    """
    if value is None:
        return default
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


# =========================
# جمع الإجمالي لفاتورة
# =========================
def compute_invoice_total(items: Iterable[JournalItem | Any]) -> Decimal:
    """
    حساب إجمالي الفاتورة عبر جمع (الكمية × السعر) لكل بند.
    """
    total = Decimal("0")
    for it in items:
        qty = parse_decimal(getattr(it, "quantity", 0))
        price = parse_decimal(getattr(it, "unit_price", 0))
        total += qty * price
    return total


# =========================
# تحويل تاريخ إلى date موحد
# =========================
def _normalize_date(value: Any) -> _date:
    """
    تحويل مرن لقيمة زمنية إلى كائن `date`:
    - datetime -> date()
    - date -> نفسه
    - None/غير ذلك -> localdate()
    """
    if isinstance(value, _datetime):
        return value.date()
    if isinstance(value, _date):
        return value
    return timezone.localdate()


# =========================
# إنشاء قيد يومية محاسبي
# =========================
@transaction.atomic
def post_journal_entry(
    *,
    description: str,
    debit_account: Account,
    credit_account: Account,
    amount: Decimal | float | str,
    date: Optional[Any] = None,
    invoice: Optional[Invoice] = None,
    created_by: Optional[Any] = None,
) -> Tuple[JournalEntry, Tuple[JournalItem, JournalItem]]:
    """
    إنشاء قيد يومية يحتوي على بند مدين وبند دائن بشكل آمن وتلقائي.
    """
    amt = parse_decimal(amount)
    if amt <= 0:
        raise ValueError("المبلغ يجب أن يكون أكبر من صفر.")

    if not isinstance(debit_account, Account) or not isinstance(
        credit_account, Account
    ):
        raise ValueError("الحسابات غير صالحة.")

    date_value = _normalize_date(date)

    entry = JournalEntry.objects.create(
        date=date_value,
        description=description,
        amount=amt,
        debit=amt,
        credit=amt,
        entry_type="system",
        invoice=invoice,
        created_by=(getattr(created_by, "employee", None) if created_by else None),
    )

    debit_item = JournalItem.objects.create(
        entry=entry,
        account=debit_account,
        debit=amt,
        credit=Decimal("0"),
    )
    credit_item = JournalItem.objects.create(
        entry=entry,
        account=credit_account,
        debit=Decimal("0"),
        credit=amt,
    )

    return entry, (debit_item, credit_item)


# =========================
# عرض آمن لحقل choices
# =========================
def safe_status_display(instance: models.Model, field_name: str) -> str:
    """
    إرجاع القيمة المقروءة لحقل Choices مثل (get_status_display)، بشكل آمن.
    """
    method_name = f"get_{field_name}_display"
    method = getattr(instance, method_name, None)
    if callable(method):
        try:
            return str(method())
        except Exception:
            return str(getattr(instance, field_name, "") or "")
    return str(getattr(instance, field_name, "") or "")


# =========================
# توليد PDF من قالب HTML
# =========================
def pdf_from_template(
    template_name: str,
    context: Dict[str, Any],
    *,
    filename: str = "report.pdf",
    as_attachment: bool = False,
) -> HttpResponse:
    """
    توليد ملف PDF باستخدام قالب HTML عبر مكتبة WeasyPrint.
    """
    html = get_template(template_name).render(context)
    pdf_bytes = HTML(string=html).write_pdf()
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    disposition = "attachment" if as_attachment else "inline"
    response["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return response
