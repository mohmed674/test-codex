from contextlib import suppress

from django.contrib import admin

from apps.demand_forecasting.models import Forecast

# ✅ Auto-registered models
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Forecast)
