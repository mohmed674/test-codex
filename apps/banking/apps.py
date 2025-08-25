# apps/banking/apps.py — App config (Sprint 3 / Banking)

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BankingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.banking"
    verbose_name = _("Banking & Payments")

    def ready(self):
        # Import signals on app ready (safe import)
        from . import signals  # noqa: F401
