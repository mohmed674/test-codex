# apps/work_regulations/admin.py
from contextlib import suppress

from django.contrib import admin

from apps.work_regulations.models import EmployeeAgreement, Regulation

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Regulation)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(EmployeeAgreement)
