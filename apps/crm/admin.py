from contextlib import suppress

from django.contrib import admin

from apps.crm.models import Interaction, Lead, Opportunity

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Lead)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Interaction)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Opportunity)
