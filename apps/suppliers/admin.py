from django.contrib import admin
from apps.suppliers.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Supplier)
except admin.sites.AlreadyRegistered:
    pass