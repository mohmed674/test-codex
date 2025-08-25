from django.contrib import admin
from apps.production.models import *

# ✅ Auto-registered models
try:
    admin.site.register(ProductionOrder)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ProductionStage)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(MaterialConsumption)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(FinalProductOutput)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ProductionScanQR)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(BillOfMaterials)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(QualityCheck)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ProductVersion)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ProductionLog)
except admin.sites.AlreadyRegistered:
    pass