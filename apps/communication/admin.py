from django.contrib import admin
from apps.communication.models import *

# ✅ Auto-registered models
try:
    admin.site.register(ChatThread)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Message)
except admin.sites.AlreadyRegistered:
    pass