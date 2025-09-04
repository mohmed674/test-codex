from contextlib import suppress

from django.contrib import admin

from apps.employee_monitoring.models import Evaluation, MonitoringRecord

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(MonitoringRecord)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Evaluation)
