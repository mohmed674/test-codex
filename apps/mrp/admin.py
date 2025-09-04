from contextlib import suppress

from django.contrib import admin

from apps.mrp.models import (MaterialLine, MaterialPlanning, PlanningException,
                             ProcurementSuggestion)

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(MaterialPlanning)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(MaterialLine)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ProcurementSuggestion)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(PlanningException)
