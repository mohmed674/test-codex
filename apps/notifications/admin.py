from contextlib import suppress

from django.contrib import admin

from apps.notifications.models import Notification

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Notification)
