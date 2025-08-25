from django.apps import AppConfig

class InternalMonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.internal_monitoring'

    def ready(self):
        # ✅ تفعيل الإشعارات الذكية عند الحوادث التأديبية أو المخاطر
        import apps.internal_monitoring.signals
