from django.contrib import admin
from apps.voice_commands.models import *

# ✅ Auto-registered models
try:
    admin.site.register(VoiceCommand)
except admin.sites.AlreadyRegistered:
    pass