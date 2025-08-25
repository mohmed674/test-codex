# PATH: D:\ERP_CORE\ai_decision\apps.py
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AiDecisionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_decision'
    label = 'ai_decision'
    verbose_name = _("الذكاء الاصطناعي (Copilot)")

    def ready(self):
        # استيراد إشارات التطبيق إن وجدت — آمن ولا يسبب كسر عند عدم وجود الملف
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
