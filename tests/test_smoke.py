# tests/test_smoke.py — فحوصات صحة البيئة وتشغيل Django/Pytest

import os
import uuid
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model

# نحتاج قاعدة البيانات في معظم الاختبارات هنا
pytestmark = pytest.mark.django_db(transaction=True)


def test_settings_module_and_urls():
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "config.pytest_settings"
    assert settings.ROOT_URLCONF in ("config.test_urls", "config.urls")


def test_allowed_hosts_and_middleware():
    assert "testserver" in settings.ALLOWED_HOSTS
    assert any(m.endswith("AuthenticationMiddleware") for m in settings.MIDDLEWARE)
    assert any(m.endswith("CsrfViewMiddleware") for m in settings.MIDDLEWARE)


def test_templates_context_processors():
    cps = []
    for tpl in settings.TEMPLATES:
        cps.extend(tpl.get("OPTIONS", {}).get("context_processors", []))
    assert "django.template.context_processors.request" in cps
    assert "django.contrib.auth.context_processors.auth" in cps


def test_ok_endpoint(client):
    r = client.get("/__ok__")
    assert r.status_code == 200
    assert r.json().get("ok") is True


def test_admin_access(client):
    r = client.get("/admin/")
    assert r.status_code in (200, 302)
    if r.status_code == 302:
        assert "/admin/login" in r.headers.get("Location", "")


def test_user_model_crud():
    User = get_user_model()
    u = User.objects.create_user(
        username=f"u_{uuid.uuid4().hex[:8]}",
        email=f"u_{uuid.uuid4().hex[:8]}@example.com",
        password="test-pass-123",
    )
    assert User.objects.filter(pk=u.pk).exists()


def test_test_database_naming():
    engine = settings.DATABASES["default"]["ENGINE"]
    test_name = settings.DATABASES["default"].get("TEST", {}).get("NAME") or settings.DATABASES["default"].get("NAME")
    if "sqlite3" not in engine:
        assert str(test_name).startswith("test_")


def test_apps_collection_when_apps_dir_exists():
    base_dir = getattr(settings, "BASE_DIR", Path(__file__).resolve().parents[1])
    apps_dir = Path(base_dir) / "apps"
    if apps_dir.exists():
        assert any(a.startswith("apps.") for a in settings.INSTALLED_APPS)


def test_admin_has_user_registered():
    User = get_user_model()
    assert User in admin.site._registry
