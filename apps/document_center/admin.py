from django.contrib import admin
from apps.document_center.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Document)
except admin.sites.AlreadyRegistered:
    pass