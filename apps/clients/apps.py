from __future__ import annotations

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ClientsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.clients"
    verbose_name = _("العملاء والشركاء")

    def ready(self) -> None:
        # تحميل الإشارات إن وُجدت
        try:
            import apps.clients.signals  # noqa: F401
        except Exception:
            # تجاهل أي خطأ عند تحميل الإشارات لعدم تعطيل بدء التشغيل
            return
