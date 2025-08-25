from django.contrib import admin
from apps.internal_monitoring.models import *

# ✅ Auto-registered models
try:
    admin.site.register(InventoryDiscrepancy)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(SuspiciousActivity)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(RiskIncident)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ReportLog)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(DisciplinaryAction)
except admin.sites.AlreadyRegistered:
    pass