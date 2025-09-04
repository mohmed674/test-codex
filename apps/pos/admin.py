from contextlib import suppress

from django.contrib import admin

from apps.pos.models import POSOrder, POSOrderItem, POSSession

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(POSSession)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(POSOrder)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(POSOrderItem)
