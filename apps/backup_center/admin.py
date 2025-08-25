from django.contrib import admin
from apps.backup_center.models import *

# ✅ Auto-registered models
try:
    admin.site.register(BackupRecord)
except admin.sites.AlreadyRegistered:
    pass