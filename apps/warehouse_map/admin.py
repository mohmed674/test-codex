# apps/warehouse_map/admin.py
from contextlib import suppress

from django.contrib import admin

from apps.warehouse_map.models import Location, Zone

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Zone)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Location)
