from contextlib import suppress

from django.contrib import admin

from apps.sales.models import (ClientActivity, ClientPointsLog,
                               ProductSalesAnalysis, SaleInvoice, SaleItem,
                               SalesPerformance, SmartSalesSuggestion)

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(SaleInvoice)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(SaleItem)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ClientPointsLog)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(SalesPerformance)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ProductSalesAnalysis)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ClientActivity)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(SmartSalesSuggestion)
