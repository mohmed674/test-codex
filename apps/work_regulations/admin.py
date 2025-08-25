from django.contrib import admin
from apps.work_regulations.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Regulation)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(EmployeeAgreement)
except admin.sites.AlreadyRegistered:
    pass