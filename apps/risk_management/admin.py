from django.contrib import admin
from apps.risk_management.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Risk)
except admin.sites.AlreadyRegistered:
    pass