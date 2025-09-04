from contextlib import suppress

from django.contrib import admin

from apps.risk_management.models import Risk

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Risk)
