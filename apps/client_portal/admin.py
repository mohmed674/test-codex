from django.contrib import admin
from apps.client_portal.models import *

# ✅ Auto-registered models
try:
    admin.site.register(ClientAccess)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(SupportTicket)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(SupportResponse)
except admin.sites.AlreadyRegistered:
    pass