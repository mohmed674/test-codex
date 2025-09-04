# apps/tracking/admin.py
from contextlib import suppress

from django.contrib import admin

from apps.tracking.models import ProductTracking, ProductTrackingMovement

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ProductTracking)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ProductTrackingMovement)
