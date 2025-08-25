from django.contrib import admin
from apps.shipping.models import *

# ✅ Auto-registered models
try:
    admin.site.register(ShippingCompany)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Shipment)
except admin.sites.AlreadyRegistered:
    pass