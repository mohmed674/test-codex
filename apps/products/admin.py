from django.contrib import admin
from apps.products.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Product)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(FinishedProduct)
except admin.sites.AlreadyRegistered:
    pass