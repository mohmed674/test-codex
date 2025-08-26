# ERP_CORE/departments/apps.py
from django.apps import AppConfig

class DepartmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.departments'
    verbose_name = 'apps.departments'

    def ready(self):
        try:
            import apps.departments.signals  # type: ignore  # ✅ تحميل الإشارات عند توافرها
            import apps.departments.ai       # type: ignore  # ✅ تحميل منطق الذكاء الاصطناعي
        except Exception:
            # أثناء الاختبارات قد لا تتوافر تبعيات ai_decision وغيرها
            pass
