from django.contrib import admin
from apps.notifications.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Notification)
except admin.sites.AlreadyRegistered:
    pass