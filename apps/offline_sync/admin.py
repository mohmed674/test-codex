from contextlib import suppress

from django.contrib import admin

from apps.offline_sync.models import OfflineSyncLog

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(OfflineSyncLog)
