from django.contrib import admin
from apps.whatsapp_bot.models import *

# ✅ Auto-registered models
try:
    admin.site.register(WhatsAppOrder)
except admin.sites.AlreadyRegistered:
    pass