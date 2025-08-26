# config/pytest_settings.py — إعدادات مبسّطة للاختبارات عبر Pytest

"""تهيئة دنيا لتشغيل اختبارات Django دون الاعتماد على كامل إعدادات المشروع."""

from pathlib import Path
import os


# ✳️ الجذر
BASE_DIR = Path(__file__).resolve().parent.parent


# ✅ تطبيقات Django الأساسية + ما يلزم للاختبارات
BASE_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

PROJECT_APPS = [
    "apps.employees",
    "apps.employee_monitoring",
    "apps.survey",
    "apps.media",  # تطبيق وسائط مصغّر للاختبارات
    "apps.departments",
]

INSTALLED_APPS = BASE_APPS + PROJECT_APPS


# ✅ ميدلوير أساسي
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]


# ✅ مسار عناوين مبسّط للاختبارات
ROOT_URLCONF = "config.test_urls"


# ✅ القوالب
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    }
]


# ✅ إعدادات أساسية أخرى
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / ".pytest_media"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "pytest-secret-key")
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ✅ تبسيط الاختبارات
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
AUTH_PASSWORD_VALIDATORS = []
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "pytest-cache",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

