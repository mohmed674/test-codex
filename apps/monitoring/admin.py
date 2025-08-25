from django.contrib import admin
from apps.monitoring.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Client)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(DistributionOrder)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Shipment)
except admin.sites.AlreadyRegistered:
    pass