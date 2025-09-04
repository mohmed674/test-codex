from contextlib import suppress

from django.contrib import admin

from apps.payroll.models import (Advance, AttendanceRecord, HistoricalPayment,
                                 MonthlyIncentive, PaymentRecord,
                                 PolicySetting, Salary)

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Salary)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Advance)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(PaymentRecord)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(HistoricalPayment)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(AttendanceRecord)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(MonthlyIncentive)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(PolicySetting)
