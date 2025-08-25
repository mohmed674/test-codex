from django.contrib import admin
from apps.rfq.models import *

# ✅ Auto-registered models
try:
    admin.site.register(RFQ)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(RFQItem)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(RFQResponse)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(RFQResponseItem)
except admin.sites.AlreadyRegistered:
    pass