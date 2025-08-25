from django.contrib import admin
from apps.warehouse_map.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Zone)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Location)
except admin.sites.AlreadyRegistered:
    pass