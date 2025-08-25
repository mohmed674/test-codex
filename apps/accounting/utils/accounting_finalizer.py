# ✅ ERP_CORE/accounting/utils/accounting_finalizer.py
from django.db import models
from datetime import datetime
from django.utils import timezone
from apps.accounting.models import (
    Account, JournalEntry, JournalItem, Customer, Supplier
)


def generate_next_season_label():
    current_year = timezone.now().year
    return f"{current_year+1}-Season"


def close_and_rollover_balances(confirm=True, include_customers=True, include_suppliers=True):
    """
    ✅ إغلاق الحسابات وتدوير الأرصدة والموردين/العملاء للموسم الجديد.
    """
    if not confirm:
        return "❌ لم يتم التفعيل بسبب عدم التأكيد."

    season_label = generate_next_season_label()
    today = timezone.now().date()
    summary_entry = JournalEntry.objects.create(
        date=today,
        description=f"تدوير أرصدة الموسم السابق إلى {season_label}",
        debit=0,
        credit=0,
    )

    accounts = Account.objects.all()
    for acc in accounts:
        debit_total = JournalItem.objects.filter(account=acc).aggregate(total=models.Sum('debit'))['total'] or 0
        credit_total = JournalItem.objects.filter(account=acc).aggregate(total=models.Sum('credit'))['total'] or 0
        balance = debit_total - credit_total

        if abs(balance) > 0.01:
            if balance > 0:
                JournalItem.objects.create(entry=summary_entry, account=acc, debit=balance, credit=0)
            else:
                JournalItem.objects.create(entry=summary_entry, account=acc, debit=0, credit=abs(balance))

    result = ["✅ تم تدوير الأرصدة"]

    if include_customers:
        customers = Customer.objects.all()
        for customer in customers:
            customer.pk = None  # Clone
            customer.save()
        result.append("✅ تم نسخ العملاء إلى الموسم التالي")

    if include_suppliers:
        suppliers = Supplier.objects.all()
        for supplier in suppliers:
            supplier.pk = None
            supplier.save()
        result.append("✅ تم نسخ الموردين إلى الموسم التالي")

    return " / ".join(result)
