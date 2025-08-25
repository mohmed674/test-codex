from django.contrib import admin
from apps.offline_sync.models import *

# ✅ Auto-registered models
try:
    admin.site.register(OfflineSyncLog)
except admin.sites.AlreadyRegistered:
    pass