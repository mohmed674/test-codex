# config/settings.py — ERP Smart System (Hardened + Global + Banking + Site)

import os
from pathlib import Path
from dotenv import load_dotenv  # ✅ تحميل ملف البيئة

# ── Base Directory + تحميل .env ────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')  # ✅ تحميل ملف .env من جذر المشروع

# تم إزالة طباعة بيانات الاتصال لتجنب كشف المتغيرات السرية


from celery.schedules import crontab
from django.contrib.messages import constants as message_constants
from django.utils.translation import gettext_lazy as _

# ── Environment-driven core settings ───────────────────────────────────────────
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY environment variable is not set")
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

def _csv_env(name, default=''):
    return [v.strip() for v in os.environ.get(name, default).split(',') if v.strip()]

ALLOWED_HOSTS = _csv_env('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1]')

INSTALLED_APPS = [
    'apps.plm',
    'widget_tweaks',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_celery_results',
    'rest_framework',
    'django_filters',
    'django_celery_beat',
    'corsheaders',
    'colorfield',
    # 'core',  ⛔ تمت إزالته
    'apps.employees',
    'apps.attendance',
    'apps.evaluation',
    'apps.payroll',
    'apps.departments',
    'apps.discipline',
    'apps.employee_monitoring',
    'apps.production',
    'apps.products',
    'apps.inventory',
    'apps.survey',
    'apps.tracking',
    'apps.media.apps.MediaConfig',
    'apps.maintenance',
    'apps.monitoring',
    'apps.internal_monitoring',
    'apps.pattern',
    'apps.voice_commands',
    'apps.clients',
    'apps.sales',
    'apps.purchases',
    'apps.accounting',
    'apps.ai_decision',
    'apps.whatsapp_bot',
    'apps.theme_manager',
    'apps.themes',
    'apps.dark_mode',
    'apps.bi',
    'apps.campaigns',
    'apps.client_portal',
    'apps.contracts',
    'apps.crm',
    'apps.legal',
    'apps.mobile',
    'apps.notifications',
    'apps.offline_sync',
    'apps.pos',
    'apps.projects',
    'apps.risk_management',
    'apps.shipping',
    'apps.suppliers',
    'apps.support',
    'apps.dashboard_center',
    'apps.api_gateway',
    'apps.asset_lifecycle',
    'apps.backup_center',
    'apps.communication',
    'apps.demand_forecasting',
    'apps.document_center',
    'apps.expenses',
    'apps.internal_bot',
    'apps.knowledge_center',
    'apps.mrp',
    'apps.recruitment',
    'apps.rfq',
    'apps.vendor_portal',
    'apps.warehouse_map',
    'apps.work_regulations',
    'apps.workflow',
    'apps.qms',
    'apps.audit_out',
    'apps.docs',
    'apps.templates',
    'apps.site',
    'apps.banking',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'core.middleware.NoCacheHTMLMiddleware',  ⛔ تمت إزالته
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.theme_manager.middleware.ThemeMiddleware',
    # 'core.middleware.global_context.GlobalContextMiddleware',  ⛔ تمت إزالته
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'core' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                # 'core.middleware.global_context.global_context_processor',  ⛔ تمت إزالته
            ],
        },
    },
]

# ── Database (env-driven) ─────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DJANGO_DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DJANGO_DB_NAME', 'erp_core_db'),
        'USER': os.environ.get('DJANGO_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', ''),
        'HOST': os.environ.get('DJANGO_DB_HOST', 'localhost'),
        'PORT': os.environ.get('DJANGO_DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('ar', _('العربية')),
    ('en', _('English')),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365
LANGUAGE_COOKIE_HTTPONLY = True
LANGUAGE_COOKIE_SAMESITE = 'Lax'
LANGUAGE_COOKIE_PATH = '/'

STATIC_URL = '/static/'
STATICFILES_DIRS = []
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

from pathlib import Path as _Path
for _p in (STATIC_ROOT, MEDIA_ROOT):
    try:
        _Path(_p).mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TIMEZONE = 'Africa/Cairo'
CELERY_ENABLE_UTC = True
CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_CACHE_BACKEND = 'default'
CELERY_RESULT_EXTENDED = True

CELERY_BEAТ_SCHEDULE = {
    'daily-analyze-sales': {
        'task': 'apps.ai_decision.tasks.analyze_product_sales',
        'schedule': crontab(hour=2, minute=0),
        'args': ('daily',),
        'options': {'expires': 3600}
    },
    'weekly-analyze-sales': {
        'task': 'apps.ai_decision.tasks.analyze_product_sales',
        'schedule': crontab(hour=3, minute=0, day_of_week='sunday'),
        'args': ('weekly',),
        'options': {'expires': 7200}
    },
    'monthly-analyze-sales': {
        'task': 'apps.ai_decision.tasks.analyze_product_sales',
        'schedule': crontab(hour=4, minute=0, day_of_month='1'),
        'args': ('monthly',),
        'options': {'expires': 10800}
    },
    'predictive-ai-sales-forecast': {
        'task': 'apps.ai_decision.tasks.predict_future_sales',
        'schedule': crontab(hour=5, minute=0),
        'options': {'expires': 3600}
    },
    'detect-stagnant-or-loss-products': {
        'task': 'apps.ai_decision.tasks.detect_stagnant_products',
        'schedule': crontab(hour=6, minute=0, day_of_week='friday'),
        'options': {'expires': 3600}
    },
    'send-daily-ai-alerts': {
        'task': 'apps.ai_decision.tasks.send_daily_alerts_to_admin',
        'schedule': crontab(hour=7, minute=0),
        'options': {'expires': 3600}
    },
    'monthly-employee-incentives': {
        'task': 'apps.employees.tasks.run_monthly_incentive_calculation',
        'schedule': crontab(hour=3, minute=0, day_of_month=1),
        'options': {'expires': 7200}
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'True') == 'True'

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.example.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'erp@yourdomain.com')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@yourdomain.com')

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_TAGS = {
    message_constants.DEBUG: 'secondary',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}

LOGIN_URL = '/admin/login/'
LOGOUT_REDIRECT_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'

SAP_SYSTEM_NAME = _("ERP Smart System")
ENABLE_AI_NOTIFICATIONS = True
ENABLE_MONITORING_LOGS = True
ENABLE_AUTO_ALERTS = True
ENABLE_MULTI_LANGUAGE = True
DEFAULT_COUNTRY = "Egypt"

WHATSAPP_API_URL = os.environ.get('WHATSAPP_API_URL', 'https://api.ultramsg.com/instanceXXXX/messages/chat')
WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN', '')
WHATSAPP_TO = os.environ.get('WHATSAPP_TO', '')

PWA_SW_URL = '/sw.js'
PWA_OFFLINE_URL = '/offline.html'
FAVICON_STATIC_PATH = 'icons/favicon.ico'

CSRF_TRUSTED_ORIGINS = _csv_env('DJANGO_CSRF_TRUSTED_ORIGINS', '')

try:
    from core.settings_global import *  # noqa: F401,F403
except Exception:
    pass

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    LANGUAGE_COOKIE_SECURE = True
