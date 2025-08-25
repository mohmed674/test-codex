from django.contrib import admin
from apps.employee_monitoring.models import *

# ✅ Auto-registered models
try:
    admin.site.register(MonitoringRecord)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Evaluation)
except admin.sites.AlreadyRegistered:
    pass