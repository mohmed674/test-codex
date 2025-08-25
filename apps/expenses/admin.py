from django.contrib import admin
from apps.expenses.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Expense)
except admin.sites.AlreadyRegistered:
    pass