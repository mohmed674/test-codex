from contextlib import suppress

from django.contrib import admin

from apps.plm.models import (Bom, BomLine, ChangeRequest, ChangeRequestItem,
                             LifecycleStage, PLMDocument, ProductLifecycle,
                             ProductTemplate, ProductVersion)

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(PLMDocument)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ProductTemplate)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ProductVersion)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(LifecycleStage)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ProductLifecycle)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Bom)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(BomLine)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ChangeRequest)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ChangeRequestItem)
