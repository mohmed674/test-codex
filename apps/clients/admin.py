from contextlib import suppress

from django.contrib import admin

from apps.clients.models import Address, Client, Customer, Partner

# ✅ Auto-registered models with safe context handling
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Partner)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Address)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Customer)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Client)
