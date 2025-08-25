from django.contrib import admin
from apps.legal.models import *

# ✅ Auto-registered models
try:
    admin.site.register(LegalCase)
except admin.sites.AlreadyRegistered:
    pass