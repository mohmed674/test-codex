from contextlib import suppress

from django.contrib import admin

from apps.maintenance.models import Machine, MaintenanceLog, MaintenanceRequest

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Machine)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(MaintenanceLog)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(MaintenanceRequest)
