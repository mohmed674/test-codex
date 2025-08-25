from django.contrib import admin
from apps.mrp.models import *

# ✅ Auto-registered models
try:
    admin.site.register(MaterialPlanning)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(MaterialLine)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ProcurementSuggestion)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(PlanningException)
except admin.sites.AlreadyRegistered:
    pass