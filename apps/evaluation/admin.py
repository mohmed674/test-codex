from contextlib import suppress

from django.contrib import admin

from apps.evaluation.models import Evaluation, LatenessAbsence

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Evaluation)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(LatenessAbsence)
