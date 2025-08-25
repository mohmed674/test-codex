# config/pytest_settings.py — isolated settings for pytest

from .settings import *  # noqa
from pathlib import Path
from typing import List, Optional
import importlib
import os

# ✳️ الجذر
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ تطبيقات Django الأساسية (سيتم دمجها مع الموجودة في settings الأساسية)
BASE_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# ✅ تجميع جميع تطبيقات المشروع تلقائيًا من مجلد apps/
def collect_all_apps(base_path: Path, exclude: Optional[List[str]] = None) -> List[str]:
    apps_dir = base_path / "apps"
    result: List[str] = []
    if not apps_dir.exists():
        return result
    for item in apps_dir.iterdir():
        if item.is_dir() and (item / "apps.py").exists():
            app_name = f"apps.{item.name}"
            if not exclude or app_name not in exclude:
                result.append(app_name)
    return sorted(result)

# ✅ رصد تطبيق core سواء كان في الجذر أو ضمن apps/
def resolve_core_app(base_path: Path) -> Optional[str]:
    if (base_path / "apps" / "core" / "apps.py").exists():
        return "apps.core"
    if (base_path / "core" / "apps.py").exists():
        return "core"
    return None

_project_apps = collect_all_apps(BASE_DIR)
_core_app = resolve_core_app(BASE_DIR)
if _core_app and _core_app not in _project_apps:
    _project_apps.insert(0, _core_app)

PROJECT_APPS = _project_apps

# ✅ دمج INSTALLED_APPS من الإعدادات الأساسية + الأساسية + تطبيقات المشروع (مع إزالة التكرارات مع الحفاظ على الترتيب)
_BASE_INSTALLED_APPS = list(globals().get("INSTALLED_APPS", []))
INSTALLED_APPS = list(dict.fromkeys(_BASE_INSTALLED_APPS + BASE_APPS + PROJECT_APPS))

# ✅ ميدلوير: استخدم الموجود في الإعدادات الأساسية وإلا وفّر مجموعة افتراضية آمنة
MIDDLEWARE = list(globals().get("MIDDLEWARE", [])) or [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# ✅ مسار عناوين الاختبار مع آلية سقوط تلقائية إذا لم يتوفر test_urls
try:
    importlib.import_module("config.test_urls")
    ROOT_URLCONF = "config.test_urls"
except Exception:
    ROOT_URLCONF = "config.urls"  # fallback آمن

# ✅ القوالب (استخدم الأساسية إن كانت معرفة)
TEMPLATES = globals().get(
    "TEMPLATES",
    [
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
        },
    ],
)

# ✅ أساسيّات بيئة الاختبار
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / ".pytest_media"

# ✅ مفاتيح/سماحيات آمنة للاختبار
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", globals().get("SECRET_KEY", "pytest-secret-key"))
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# ✅ قاعدة البيانات: تأكيد استخدام test_… تلقائيًا وعدم التعارض
if "DATABASES" in globals() and "default" in DATABASES:
    _default = DATABASES["default"]
    _test_cfg = dict(_default.get("TEST", {}))
    _base_name = _test_cfg.get("NAME") or _default.get("NAME")
    if _base_name and not str(_base_name).startswith("test_"):
        _test_cfg["NAME"] = f"test_{_base_name}"
    DATABASES["default"]["TEST"] = _test_cfg

# ✅ تسريع الاختبارات وتقليل الاعتمادات الخارجية
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
AUTH_PASSWORD_VALIDATORS = []
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "pytest-cache",
    }
}

# ✅ تجنب تحذيرات حقول المفاتيح
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
