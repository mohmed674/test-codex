from contextlib import suppress

from django.contrib import admin

from apps.purchases.models import (PurchaseInvoice, PurchaseItem,
                                   PurchaseOrder, PurchaseRequest)

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(PurchaseRequest)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(PurchaseItem)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(PurchaseOrder)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(PurchaseInvoice)
