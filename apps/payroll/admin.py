from django.contrib import admin
from apps.payroll.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Salary)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Advance)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(PaymentRecord)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(HistoricalPayment)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(AttendanceRecord)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(MonthlyIncentive)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(PolicySetting)
except admin.sites.AlreadyRegistered:
    pass