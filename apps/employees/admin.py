from contextlib import suppress

from django.contrib import admin

from apps.employees.models import (AttendanceRecord, Department, Employee,
                                   MonthlyIncentive)

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Department)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Employee)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(AttendanceRecord)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(MonthlyIncentive)
