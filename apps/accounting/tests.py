# ERP_CORE/accounting/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User, Permission
from apps.accounting.models import (
    Customer, Supplier, SalesInvoice, PurchaseInvoice,
    InvoiceItem, JournalEntry, JournalItem, Account,
    AccountingSuggestionLog
)
from apps.accounting.ai_accounting_assistant import AIAccountingAssistant


class AccountingModelsTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(name="Test Customer")
        self.supplier = Supplier.objects.create(name="Test Supplier")
        self.account_asset = Account.objects.create(name="Asset Account", code="1000", type="asset")
        self.account_expense = Account.objects.create(name="Expense Account", code="2000", type="expense")

    def test_customer_str(self):
        self.assertEqual(str(self.customer), "Test Customer")

    def test_supplier_str(self):
        self.assertEqual(str(self.supplier), "Test Supplier")

    def test_account_str(self):
        self.assertIn("Asset Account", str(self.account_asset))

    def test_journal_entry_creation(self):
        entry = JournalEntry.objects.create(
            description="Test Entry",
            amount=Decimal('100.00'),
            debit=Decimal('100.00'),
            credit=Decimal('0.00'),
            date=timezone.now()
        )
        self.assertEqual(entry.description, "Test Entry")
        self.assertEqual(entry.amount, Decimal('100.00'))

    def test_journal_item_creation(self):
        entry = JournalEntry.objects.create(
            description="Entry for Items",
            amount=Decimal('100.00'),
            debit=Decimal('100.00'),
            credit=Decimal('0.00'),
            date=timezone.now()
        )
        item = JournalItem.objects.create(
            entry=entry,
            account=self.account_asset,
            debit=Decimal('100.00'),
            credit=Decimal('0.00')
        )
        self.assertEqual(item.account.name, "Asset Account")


class AccountingViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user1', password='pass1234')
        self.user.user_permissions.add(Permission.objects.get(codename='view_journalentry'))
        self.user.user_permissions.add(Permission.objects.get(codename='add_journalentry'))
        self.client.login(username='user1', password='pass1234')

        self.customer = Customer.objects.create(name="Customer 1")
        self.supplier = Supplier.objects.create(name="Supplier 1")

    def test_home_view(self):
        response = self.client.get(reverse('accounting:accounting_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "مرحبًا بك في نظام المحاسبة")

    def test_supplier_list_view(self):
        response = self.client.get(reverse('accounting:supplier_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Supplier 1")

    def test_customer_list_view(self):
        response = self.client.get(reverse('accounting:customer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Customer 1")

    def test_create_sales_invoice_view_get(self):
        response = self.client.get(reverse('accounting:create_sales_invoice'))
        self.assertEqual(response.status_code, 200)

    def test_create_purchase_invoice_view_get(self):
        response = self.client.get(reverse('accounting:create_purchase_invoice'))
        self.assertEqual(response.status_code, 200)

    def test_journal_dashboard_view(self):
        response = self.client.get(reverse('accounting:journal_dashboard'))
        self.assertEqual(response.status_code, 200)


class AIAccountingAssistantTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='aiuser', password='testpass')

        self.debit_account = Account.objects.create(name="Inventory Account", code="3000", type="asset")
        self.credit_account = Account.objects.create(name="Accounts Payable Account", code="4000", type="liability")

    def test_suggest_accounts(self):
        assistant = AIAccountingAssistant(user=self.user)
        debit, credit = assistant.suggest_accounts("شراء خامات لتصنيع", 1000, "شراء خامات")
        self.assertEqual(debit.name, "Inventory Account")
        self.assertEqual(credit.name, "Accounts Payable Account")

    def test_validate_entry(self):
        assistant = AIAccountingAssistant(user=self.user)
        self.assertTrue(assistant.validate_entry(self.debit_account, self.credit_account, 1000))
        self.assertFalse(assistant.validate_entry(None, self.credit_account, 1000))
        self.assertFalse(assistant.validate_entry(self.debit_account, None, 1000))
        self.assertFalse(assistant.validate_entry(self.debit_account, self.credit_account, -10))

    def test_generate_entry_creates_journal_entry(self):
        assistant = AIAccountingAssistant(user=self.user)
        entry = assistant.generate_entry("شراء خامات", 5000, "شراء خامات")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.description, "شراء خامات")
        self.assertEqual(entry.amount, Decimal('5000'))

        # تحقق من وجود بنود قيد صحيحة
        items = entry.items.all()
        self.assertEqual(items.count(), 2)
        debit_item = items.filter(debit__gt=0).first()
        credit_item = items.filter(credit__gt=0).first()
        self.assertEqual(debit_item.account.name, "Inventory Account")
        self.assertEqual(credit_item.account.name, "Accounts Payable Account")
