from django.contrib import admin
from apps.contracts.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Contract)
except admin.sites.AlreadyRegistered:
    pass