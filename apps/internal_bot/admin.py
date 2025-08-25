from django.contrib import admin
from apps.internal_bot.models import *

# ✅ Auto-registered models
try:
    admin.site.register(BotMessage)
except admin.sites.AlreadyRegistered:
    pass