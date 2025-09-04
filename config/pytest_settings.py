# config/pytest_settings.py — isolated settings for pytest (dedupe by app label)

import importlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, cast

from .settings import *  # noqa: F401,F403

# ✳️ الجذر
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ تطبيقات Django الأساسية (تُدمج مع الموجودة في settings الأساسية)
BASE_APPS: List[str] = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]


# ✅ أدوات مساعدة لاستخراج label وإزالة التكرار حسب الـlabel
def app_label_from_entry(s: str) -> str:
    # أمثلة:
    # "apps.plm" → "plm"
    # "apps.media.apps.MediaConfig" → "media"
    # "core.apps.CoreConfig" → "core"
    if ".apps." in s:
        base = s.split(".apps.")[0]
        return base.split(".")[-1]
    return s.split(".")[-1]


def dedupe_by_label(apps: List[str]) -> List[str]:
    out: List[str] = []
    seen: Set[str] = set()
    for a in apps:
        label = app_label_from_entry(a)
        if label in seen:
            continue
        seen.add(label)
        out.append(a)
    return out


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


# ⚙️ ابدأ من INSTALLED_APPS الأساسية ثم طَبّق تسوية صريحة للـ core
_BASE_INSTALLED_APPS = list(globals().get("INSTALLED_APPS", []))

# أزل أي إدخالات تحمل label = core ثم أضف الإدخال الموحد مرّة واحدة
_BASE_INSTALLED_APPS = [
    a for a in _BASE_INSTALLED_APPS if app_label_from_entry(a) != "core"
]
_BASE_INSTALLED_APPS.append("core.apps.CoreConfig")

# اجمع تطبيقات apps/* واستبعد أي إدخال label=core (لتفادي التكرار)
_project_apps = collect_all_apps(BASE_DIR)
_project_apps = [a for a in _project_apps if app_label_from_entry(a) != "core"]

# تطبيع media إلى AppConfig صريح
_project_apps = [
    "apps.media.apps.MediaConfig" if a == "apps.media" else a for a in _project_apps
]

# ✅ التركيب النهائي مع إزالة التكرار بحسب الـlabel
INSTALLED_APPS: List[str] = dedupe_by_label(
    _BASE_INSTALLED_APPS + BASE_APPS + _project_apps
)

# ✅ Middleware
MIDDLEWARE = list(globals().get("MIDDLEWARE", [])) or [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# ✅ ROOT_URLCONF مع fallback
try:
    importlib.import_module("config.test_urls")
    ROOT_URLCONF = "config.test_urls"
except Exception:
    ROOT_URLCONF = "config.urls"

# ✅ TEMPLATES
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

# ✅ أساسيات الاختبار
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / ".pytest_media"

# ✅ مفاتيح/سماحيات آمنة
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", globals().get("SECRET_KEY", "pytest-secret-key")
)
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# ✅ قاعدة البيانات: تأكيد استخدام test_… تلقائيًا (مع توضيح الأنواع لـ mypy)
if "DATABASES" in globals() and "default" in cast(Dict[str, Any], DATABASES):
    _default: Dict[str, Any] = cast(Dict[str, Any], DATABASES)["default"]
    _test_cfg: Dict[str, Any] = dict(
        cast(Dict[str, Any], _default.get("TEST", {}) or {})
    )
    _base_name: Optional[str] = cast(
        Optional[str], _test_cfg.get("NAME") or _default.get("NAME")
    )
    if _base_name and not str(_base_name).startswith("test_"):
        _test_cfg["NAME"] = f"test_{_base_name}"
    cast(Dict[str, Any], DATABASES)["default"]["TEST"] = _test_cfg

# ✅ تسريع الاختبارات
PASSWORD_HASHERS: List[str] = ["django.contrib.auth.hashers.MD5PasswordHasher"]
AUTH_PASSWORD_VALIDATORS: List[Dict[str, Any]] = []  # ← يرضي mypy
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CACHES: Dict[str, Dict[str, Any]] = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "pytest-cache",
    }
}

# ✅ تجنب تحذيرات المفاتيح
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
