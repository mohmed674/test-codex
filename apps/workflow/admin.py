# apps/workflow/admin.py
from contextlib import suppress

from django.contrib import admin

from apps.workflow.models import WorkflowRule

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(WorkflowRule)
