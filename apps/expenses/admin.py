from contextlib import suppress

from django.contrib import admin

from apps.expenses.models import Expense

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Expense)
