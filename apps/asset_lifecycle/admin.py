from django.contrib import admin
from apps.asset_lifecycle.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Asset)
except admin.sites.AlreadyRegistered:
    pass