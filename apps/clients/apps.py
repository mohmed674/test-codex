from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ClientsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'apps.clients'
    verbose_name = _("العملاء والشركاء")

    def ready(self):
        try:
            import apps.clients.signals  # تحميل الإشارات
        except Exception:
            pass
