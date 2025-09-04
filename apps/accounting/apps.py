# apps/accounting/apps.py
from contextlib import suppress

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounting"
    verbose_name = _("📊 النظام المحاسبي")

    def ready(self) -> None:
        """
        تحميل إشارات التطبيق تلقائيًا عند تشغيله.
        """
        with suppress(Exception):
            import apps.accounting.signals  # noqa: F401
