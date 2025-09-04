from contextlib import suppress

from django.contrib import admin

from apps.rfq.models import RFQ, RFQItem, RFQResponse, RFQResponseItem

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(RFQ)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(RFQItem)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(RFQResponse)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(RFQResponseItem)
