# apps/backup_center/admin.py
"""Admin site registrations for backup_center.

- Removes star imports to satisfy flake8 (F403/F405).
- Uses contextlib.suppress for idempotent registration without noisy try/except.
- Keeps behavior intact: ensure BackupRecord is registered to Django admin.
"""

from __future__ import annotations

from contextlib import suppress

from django.contrib import admin

from apps.backup_center.models import BackupRecord

# ✅ Idempotent registration; avoids AlreadyRegistered errors on reloads/tests
with suppress(admin.sites.AlreadyRegistered):
    admin.site.register(BackupRecord)
