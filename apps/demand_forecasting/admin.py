from django.contrib import admin
from apps.demand_forecasting.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Forecast)
except admin.sites.AlreadyRegistered:
    pass