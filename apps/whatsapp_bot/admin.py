# apps/whatsapp_bot/admin.py
from contextlib import suppress

from django.contrib import admin

from apps.whatsapp_bot.models import WhatsAppOrder

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(WhatsAppOrder)
