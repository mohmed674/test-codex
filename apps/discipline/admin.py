from django.contrib import admin
from apps.discipline.models import *

# ✅ Auto-registered models
try:
    admin.site.register(DisciplineRecord)
except admin.sites.AlreadyRegistered:
    pass