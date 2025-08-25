from django.contrib import admin
from apps.accounting.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Supplier)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Customer)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(PaymentMethod)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(PaymentOrder)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Asset)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Expense)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Invoice)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Payment)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Account)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(JournalEntry)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(JournalItem)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(AccountingSuggestionLog)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(BillOfMaterial)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ManufacturingOrder)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(SupplierInvoice)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(SalesInvoice)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(PurchaseInvoice)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(InvoiceItem)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(CashTransaction)
except admin.sites.AlreadyRegistered:
    pass