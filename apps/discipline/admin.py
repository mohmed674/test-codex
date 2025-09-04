from contextlib import suppress

from django.contrib import admin

from apps.discipline.models import DisciplineRecord

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(DisciplineRecord)
