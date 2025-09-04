# apps/attendance/admin.py
from contextlib import suppress

from django.contrib import admin

from apps.attendance.models import Attendance

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Attendance)
