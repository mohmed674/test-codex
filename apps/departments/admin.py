from django.contrib import admin
from apps.departments.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Department)
except admin.sites.AlreadyRegistered:
    pass