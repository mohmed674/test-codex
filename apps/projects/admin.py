from contextlib import suppress

from django.contrib import admin

from apps.projects.models import Project, Task

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Project)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Task)
