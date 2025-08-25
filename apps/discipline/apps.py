from django.apps import AppConfig

class DisciplineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.discipline'

    def ready(self):
        import apps.discipline.signals  # ✅ تحميل إشارات الذكاء والتحليل الذاتي تلقائيًا
        import apps.discipline.ai       # ✅ تحميل منطق الذكاء الاصطناعي للعقوبات تلقائيًا
