from django.contrib import admin
from apps.plm.models import *

# ✅ Auto-registered models
try:
    admin.site.register(PLMDocument)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ProductTemplate)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ProductVersion)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(LifecycleStage)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ProductLifecycle)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Bom)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(BomLine)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ChangeRequest)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(ChangeRequestItem)
except admin.sites.AlreadyRegistered:
    pass