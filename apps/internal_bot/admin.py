from contextlib import suppress

from django.contrib import admin

from apps.internal_bot.models import BotMessage

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(BotMessage)
