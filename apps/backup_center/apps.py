from django.apps import AppConfig

class BackupCenterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.backup_center'

    def ready(self):
        import apps.backup_center.signals  # ✅ تفعيل الإشعارات تلقائيًا
