from django.contrib import admin
from apps.employees.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Department)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Employee)
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