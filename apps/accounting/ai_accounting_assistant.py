from __future__ import annotations

from contextlib import suppress
from decimal import Decimal, InvalidOperation
from typing import Any, Optional, Tuple

from django.utils import timezone

from apps.accounting.models import Account, JournalEntry, JournalItem
from apps.ai_decision.models import AIDecisionLog

_DEFAULT_DECIMAL = Decimal("0")


def _to_decimal(value: Any, default: Decimal = _DEFAULT_DECIMAL) -> Decimal:
    """تحويل آمن إلى Decimal."""
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


class AIAccountingAssistant:
    def __init__(self, user):
        self.user = user
        self.alerts: list[tuple[str, str]] = []

    def suggest_accounts(
        self, description: str, amount: Any, transaction_type: str
    ) -> Tuple[Optional[Account], Optional[Account]]:
        """
        اقتراح الحسابات بناءً على وصف القيد ونوعه (شراء، بيع، مرتبات، إلخ).
        يجب تعديل القيم لتعكس الحسابات الحقيقية في النظام.
        """
        suggestions_map = {
            "شراء خامات": ("Inventory Account", "Accounts Payable Account"),
            "بيع منتج": ("Accounts Receivable Account", "Sales Revenue Account"),
            "دفع رواتب": ("Salaries Expense Account", "Cash Account"),
            "هالك إنتاج": ("Production Loss Account", "Inventory Account"),
        }

        for key, (debit_name, credit_name) in suggestions_map.items():
            if key in (description or ""):
                debit_account = Account.objects.filter(name=debit_name).first()
                credit_account = Account.objects.filter(name=credit_name).first()
                return debit_account, credit_account

        # الحسابات الافتراضية عند عدم التطابق
        default_debit = Account.objects.filter(name="General Account").first()
        default_credit = Account.objects.filter(name="Suspense Account").first()
        return default_debit, default_credit

    def validate_entry(
        self,
        debit_account: Optional[Account],
        credit_account: Optional[Account],
        amount: Any,
    ) -> bool:
        """
        التحقق من توازن القيد والتنبيه عند الخطأ.
        """
        amt = _to_decimal(amount)
        if debit_account is None or credit_account is None:
            self._log_risk("حساب مدين أو دائن غير موجود", "High")
            return False
        if debit_account == credit_account:
            self._log_risk("قيد غير متوازن: الحساب المدين والدائن متطابقان", "High")
            return False
        if amt <= 0:
            self._log_risk("قيمة القيد غير صالحة", "Medium")
            return False
        return True

    def generate_entry(
        self, description: str, amount: Any, transaction_type: str
    ) -> Optional[JournalEntry]:
        """
        إنشاء قيد محاسبي مقترح بناءً على تحليل الذكاء الاصطناعي.
        """
        debit_account, credit_account = self.suggest_accounts(
            description, amount, transaction_type
        )

        if not self.validate_entry(debit_account, credit_account, amount):
            return None

        employee = getattr(self.user, "employee", None)
        amt = _to_decimal(amount)

        entry = JournalEntry.objects.create(
            description=description,
            amount=amt,
            date=timezone.now().date(),
            created_by=employee,
            entry_type="system",
            debit=amt,
            credit=amt,
        )

        # إنشاء البنود المدينة والدائنة
        JournalItem.objects.create(
            entry=entry,
            account=debit_account,
            debit=amt,
            credit=Decimal("0"),
        )
        JournalItem.objects.create(
            entry=entry,
            account=credit_account,
            debit=Decimal("0"),
            credit=amt,
        )

        return entry

    def _log_risk(self, message: str, level: str) -> None:
        """
        تسجيل تحذير في سجل قرارات الذكاء الاصطناعي.
        """
        with suppress(Exception):
            AIDecisionLog.objects.create(
                user=self.user,
                event_type="تنبيه محاسبي",
                risk_level=level,
                description=message,
            )
        self.alerts.append((level, message))

    def get_alerts(self) -> list[tuple[str, str]]:
        return self.alerts
