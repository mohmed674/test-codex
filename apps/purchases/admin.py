from django.contrib import admin
from apps.purchases.models import *

# ✅ Auto-registered models
try:
    admin.site.register(PurchaseRequest)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(PurchaseItem)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(PurchaseOrder)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(PurchaseInvoice)
except admin.sites.AlreadyRegistered:
    pass