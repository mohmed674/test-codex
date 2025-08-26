# ERP_CORE/departments/apps.py
from django.apps import AppConfig

class DepartmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.departments'
    verbose_name = 'apps.departments'

    def ready(self):
        try:
            import apps.departments.signals  # noqa: F401
            import apps.departments.ai       # noqa: F401
        except Exception:
            # أثناء الاختبارات قد تكون بعض التبعيات غير متاحة
            pass
