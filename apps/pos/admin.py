from django.contrib import admin
from apps.pos.models import *

# ✅ Auto-registered models
try:
    admin.site.register(POSSession)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(POSOrder)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(POSOrderItem)
except admin.sites.AlreadyRegistered:
    pass