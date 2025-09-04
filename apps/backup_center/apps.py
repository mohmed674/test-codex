# apps/backup_center/apps.py
from __future__ import annotations

from django.apps import AppConfig


class BackupCenterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.backup_center"

    def ready(self) -> None:
        # Import signals when app is ready (side-effect only)
        from apps.backup_center import signals  # noqa: F401
