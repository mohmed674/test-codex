from contextlib import suppress

from django.contrib import admin

from apps.document_center.models import Document

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Document)
