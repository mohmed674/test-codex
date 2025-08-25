from django.contrib import admin
from apps.tracking.models import *

# ✅ Auto-registered models
try:
    admin.site.register(ProductTracking)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ProductTrackingMovement)
except admin.sites.AlreadyRegistered:
    pass