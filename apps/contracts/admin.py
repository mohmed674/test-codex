from contextlib import suppress

from django.contrib import admin

from apps.contracts.models import Contract

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Contract)
