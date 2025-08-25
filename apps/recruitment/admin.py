from django.contrib import admin
from apps.recruitment.models import *

# ✅ Auto-registered models
try:
    admin.site.register(JobPosition)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Application)
except admin.sites.AlreadyRegistered:
    pass