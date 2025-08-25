from django.contrib import admin
from apps.projects.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Project)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Task)
except admin.sites.AlreadyRegistered:
    pass