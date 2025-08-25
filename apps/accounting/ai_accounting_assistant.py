# ERP_CORE/accounting/ai_accounting_assistant.py
from apps.accounting.models import JournalEntry, JournalItem, Account
from core.models import SmartAccountTemplate
from apps.ai_decision.models import AIDecisionLog
from django.utils import timezone
from decimal import Decimal

class AIAccountingAssistant:
    def __init__(self, user):
        self.user = user
        self.alerts = []

    def suggest_accounts(self, description, amount, transaction_type):
        """
        اقتراح الحسابات بناءً على وصف القيد ونوعه (شراء، بيع، مرتبات، إلخ).
        يجب تعديل القيم لتعكس الحسابات الحقيقية في النظام (FK إلى Account).
        """
        suggestions_map = {
            'شراء خامات': ('Inventory Account', 'Accounts Payable Account'),
            'بيع منتج': ('Accounts Receivable Account', 'Sales Revenue Account'),
            'دفع رواتب': ('Salaries Expense Account', 'Cash Account'),
            'هالك إنتاج': ('Production Loss Account', 'Inventory Account'),
        }

        for key, (debit_name, credit_name) in suggestions_map.items():
            if key in description:
                debit_account = Account.objects.filter(name=debit_name).first()
                credit_account = Account.objects.filter(name=credit_name).first()
                return debit_account, credit_account
        # الحساب الافتراضي عند عدم وجود تطابق
        default_debit = Account.objects.filter(name='General Account').first()
        default_credit = Account.objects.filter(name='Suspense Account').first()
        return default_debit, default_credit

    def validate_entry(self, debit_account, credit_account, amount):
        """
        التحقق من توازن القيد والتنبيه عند الخطأ.
        """
        if debit_account is None or credit_account is None:
            self._log_risk('حساب مدين أو دائن غير موجود', 'High')
            return False
        if debit_account == credit_account:
            self._log_risk('قيد غير متوازن: الحساب المدين والمقيد متطابقان', 'High')
            return False
        if amount <= 0:
            self._log_risk('قيمة القيد غير صالحة', 'Medium')
            return False
        return True

    def generate_entry(self, description, amount, transaction_type):
        """
        إنشاء قيد محاسبي مقترح بناءً على تحليل الذكاء الاصطناعي.
        """
        debit_account, credit_account = self.suggest_accounts(description, amount, transaction_type)

        if not self.validate_entry(debit_account, credit_account, amount):
            return None

        # الحصول على الموظف المرتبط بالمستخدم
        employee = getattr(self.user, 'employee', None)

        entry = JournalEntry.objects.create(
            description=description,
            amount=Decimal(amount),
            date=timezone.now(),
            created_by=employee,
            entry_type='system'  # أو 'manual' بناءً على الاستخدام
        )

        # إنشاء البنود المدينة والدائنة
        JournalItem.objects.create(
            entry=entry,
            account=debit_account,
            debit=Decimal(amount),
            credit=Decimal('0')
        )
        JournalItem.objects.create(
            entry=entry,
            account=credit_account,
            debit=Decimal('0'),
            credit=Decimal(amount)
        )

        return entry

    def _log_risk(self, message, level):
        """
        تسجيل تحذير في سجل قرارات الذكاء الاصطناعي.
        """
        AIDecisionLog.objects.create(
            user=self.user,
            event_type="تنبيه محاسبي",
            risk_level=level,
            description=message
        )
        self.alerts.append((level, message))

    def get_alerts(self):
        return self.alerts
