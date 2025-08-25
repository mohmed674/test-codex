# ERP_CORE/departments/apps.py
from django.apps import AppConfig

class DepartmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.departments'
    verbose_name = 'apps.departments'

    def ready(self):
        import apps.departments.signals  # ✅ تحميل الإشارات الذكية تلقائيًا
        import apps.departments.ai       # ✅ تحميل منطق الذكاء الاصطناعي
