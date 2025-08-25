from django.contrib import admin
from apps.clients.models import *

# ✅ Auto-registered models
try:
    admin.site.register(Partner)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Address)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Customer)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(Client)
except admin.sites.AlreadyRegistered:
    pass