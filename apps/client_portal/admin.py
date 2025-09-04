# apps/client_portal/admin.py
"""Admin site registrations for client_portal.

- Removes star imports to satisfy flake8 (F403/F405).
- Uses contextlib.suppress for idempotent registration without noisy try/except.
- Keeps behavior intact: ensure models are registered to Django admin.
"""

from __future__ import annotations

from contextlib import suppress

from django.contrib import admin

from apps.client_portal.models import (ClientAccess, SupportResponse,
                                       SupportTicket)

# ✅ Idempotent registrations; avoids AlreadyRegistered errors on reloads/tests
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(ClientAccess)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(SupportTicket)

with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(SupportResponse)
