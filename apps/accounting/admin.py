from contextlib import suppress

from django.contrib import admin

from apps.accounting.models import (Account, AccountingSuggestionLog, Asset,
                                    BillOfMaterial, CashTransaction, Customer,
                                    Expense, Invoice, InvoiceItem,
                                    JournalEntry, JournalItem,
                                    ManufacturingOrder, Payment, PaymentMethod,
                                    PaymentOrder, PurchaseInvoice,
                                    SalesInvoice, Supplier, SupplierInvoice)

_MODELS = (
    Supplier,
    Customer,
    PaymentMethod,
    PaymentOrder,
    Asset,
    Expense,
    Invoice,
    Payment,
    Account,
    JournalEntry,
    JournalItem,
    AccountingSuggestionLog,
    BillOfMaterial,
    ManufacturingOrder,
    SupplierInvoice,
    SalesInvoice,
    PurchaseInvoice,
    InvoiceItem,
    CashTransaction,
)

for _model in _MODELS:
    with suppress(admin.sites.AlreadyRegistered):
        admin.site.register(_model)
