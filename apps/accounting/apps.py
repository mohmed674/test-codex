from django.apps import AppConfig


class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounting'  # ✅ يجب أن يكون مطابقًا للمسار في settings.py

    def ready(self):
        # ✅ تحميل الإشارات الذكية تلقائيًا عند تشغيل التطبيق
        import apps.accounting.signals
