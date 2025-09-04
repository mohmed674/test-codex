from contextlib import suppress

from django.contrib import admin

from apps.communication.models import ChatThread, Message

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ChatThread)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Message)
