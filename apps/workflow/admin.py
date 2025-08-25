from django.contrib import admin
from apps.workflow.models import *

# ✅ Auto-registered models
try:
    admin.site.register(WorkflowRule)
except admin.sites.AlreadyRegistered:
    pass