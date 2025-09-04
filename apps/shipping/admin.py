# apps/shipping/admin.py
from contextlib import suppress

from django.contrib import admin

from apps.shipping.models import Shipment, ShippingCompany

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ShippingCompany)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Shipment)
