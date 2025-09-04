from contextlib import suppress

from django.contrib import admin

from apps.recruitment.models import Application, JobPosition

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(JobPosition)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Application)
