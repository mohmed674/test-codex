from django.contrib import admin
from apps.maintenance.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Machine)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(MaintenanceLog)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(MaintenanceRequest)
except admin.sites.AlreadyRegistered:
    pass