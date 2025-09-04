from contextlib import suppress

from django.contrib import admin

from apps.monitoring.models import Client, DistributionOrder, Shipment

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Client)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(DistributionOrder)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Shipment)
