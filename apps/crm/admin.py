from django.contrib import admin
from apps.crm.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Lead)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Interaction)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Opportunity)
except admin.sites.AlreadyRegistered:
    pass