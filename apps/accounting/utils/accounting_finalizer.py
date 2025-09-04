# apps/accounting/utils/accounting_finalizer.py
from django.db import models
from django.utils import timezone

from apps.accounting.models import (Account, Customer, JournalEntry,
                                    JournalItem, Supplier)


def generate_next_season_label() -> str:
    """توليد وسم الموسم التالي (مثال: 2026-Season)."""
    current_year = timezone.now().year
    return f"{current_year + 1}-Season"


def close_and_rollover_balances(
    confirm: bool = True,
    include_customers: bool = True,
    include_suppliers: bool = True,
) -> str:
    """
    ✅ إغلاق الحسابات وتدوير الأرصدة والموردين/العملاء للموسم الجديد.
    - ينشئ قيد تلخيصي للأرصدة.
    - ينسخ العملاء/الموردين إلى موسم جديد اختياريًا.
    """
    if not confirm:
        return "❌ لم يتم التفعيل بسبب عدم التأكيد."

    season_label = generate_next_season_label()
    today = timezone.now().date()

    # قيد تلخيصي لتدوير الأرصدة (القيم التفصيلية ستضاف كبنود)
    summary_entry = JournalEntry.objects.create(
        date=today,
        description=f"تدوير أرصدة الموسم السابق إلى {season_label}",
        debit=0,
        credit=0,
        # amount افتراضي = 0 حسب نموذج JournalEntry
        entry_type="system",
    )

    # تدوير أرصدة كل حساب
    accounts = Account.objects.all()
    for acc in accounts:
        debit_total = (
            JournalItem.objects.filter(account=acc).aggregate(
                total=models.Sum("debit")
            )["total"]
            or 0
        )
        credit_total = (
            JournalItem.objects.filter(account=acc).aggregate(
                total=models.Sum("credit")
            )["total"]
            or 0
        )
        balance = debit_total - credit_total

        if abs(balance) > 0.01:
            if balance > 0:
                JournalItem.objects.create(
                    entry=summary_entry,
                    account=acc,
                    debit=balance,
                    credit=0,
                )
            else:
                JournalItem.objects.create(
                    entry=summary_entry,
                    account=acc,
                    debit=0,
                    credit=abs(balance),
                )

    result_parts = ["✅ تم تدوير الأرصدة"]

    # نسخ العملاء (اختياري)
    if include_customers:
        for customer in Customer.objects.all():
            customer.pk = None  # Clone record
            customer.save()
        result_parts.append("✅ تم نسخ العملاء إلى الموسم التالي")

    # نسخ الموردين (اختياري)
    if include_suppliers:
        for supplier in Supplier.objects.all():
            supplier.pk = None
            supplier.save()
        result_parts.append("✅ تم نسخ الموردين إلى الموسم التالي")

    return " / ".join(result_parts)
