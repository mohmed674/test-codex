from contextlib import suppress

from django.contrib import admin

from apps.legal.models import LegalCase

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(LegalCase)
