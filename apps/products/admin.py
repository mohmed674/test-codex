from contextlib import suppress

from django.contrib import admin

from apps.products.models import FinishedProduct, Product

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Product)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(FinishedProduct)
