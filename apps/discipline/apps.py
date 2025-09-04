from django.apps import AppConfig


class DisciplineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.discipline"

    def ready(self):
        pass  # ✅ تحميل منطق الذكاء الاصطناعي للعقوبات تلقائيًا
