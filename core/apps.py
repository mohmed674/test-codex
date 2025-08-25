from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = "الوحدة الذكية الأساسية (Core)"

    def ready(self):
        import core.signals  # ✅ لتفعيل الإشعارات الذكية عند إنشاء المستخدمين
