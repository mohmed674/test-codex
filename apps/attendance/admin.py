from django.contrib import admin
from apps.attendance.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Attendance)
except admin.sites.AlreadyRegistered:
    pass