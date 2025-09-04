from contextlib import suppress

from django.contrib import admin

from apps.pattern.models import PatternDesign, PatternExecution, PatternPiece

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(PatternDesign)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(PatternPiece)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(PatternExecution)
