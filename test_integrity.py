import importlib
import os
from typing import Iterable, Set

import pytest
from django.apps import apps
from django.conf import settings
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from django.test import Client
from django.urls import get_resolver, set_urlconf


# عدّل القائمة حسب التطبيقات المطلوب التحقق منها مركزياً
EXPECTED_APPS: Set[str] = {
    "employees",
    "employee_monitoring",
    "survey",
    "media",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.admin",
}


def _existing_tables() -> Set[str]:
    return set(connection.introspection.table_names())


def _models_for_apps(app_labels: Iterable[str]):
    for label in app_labels:
        try:
            for model in apps.get_app_config(label).get_models():
                yield label, model
        except LookupError:
            # سيتم كشف غياب التطبيق في اختبار منفصل
            continue


def test_migration_graph_loads_without_missing_nodes():
    loader = MigrationLoader(connection)
    graph = loader.graph
    assert len(graph.nodes) > 0


@pytest.mark.django_db
def test_expected_apps_are_installed():
    installed = {cfg.name for cfg in apps.get_app_configs()}
    missing = sorted(app for app in EXPECTED_APPS if app not in installed)
    assert not missing, f"Expected apps not installed: {missing}"


@pytest.mark.django_db
def test_expected_apps_have_applied_migrations():
    loader = MigrationLoader(connection)
    applied = {name for name, _ in loader.applied_migrations}
    # تحقق أن لكل تطبيق (إن كان لديه ترحيلات) توجد ترحيلات مطبقة
    missing_any = []
    for label in EXPECTED_APPS:
        # بعض تطبيقات Django الأساسية قد تكون بدون ترحيلات محلية، نتخطاها بحذر
        has_namespace = any(k.startswith(label + ".") for k in loader.graph.nodes)
        if not has_namespace:
            continue
        has_applied = any(k.startswith(label + ".") for k in applied)
        if not has_applied:
            missing_any.append(label)
    assert not missing_any, f"Apps have no applied migrations: {missing_any}"


@pytest.mark.django_db
def test_all_models_tables_exist_for_expected_apps():
    existing = _existing_tables()
    missing_tables = []
    for label, model in _models_for_apps(EXPECTED_APPS):
        table = model._meta.db_table
        if table not in existing:
            missing_tables.append(f"{label}.{model.__name__} -> {table}")
    assert not missing_tables, f"Missing DB tables: {missing_tables}"


def test_root_urlconf_importable_and_resolves():
    urlconf = getattr(settings, "ROOT_URLCONF", None) or "config.urls"
    mod = importlib.import_module(urlconf)
    assert hasattr(mod, "urlpatterns"), f"{urlconf} must define urlpatterns"
    set_urlconf(urlconf)
    resolver = get_resolver()
    assert resolver.url_patterns, "No URL patterns found in root urlconf"


def test_admin_url_is_accessible_or_redirects_to_login():
    c = Client()
    resp = c.get("/admin/", follow=False)
    assert resp.status_code in (200, 302), f"/admin/ unexpected status: {resp.status_code}"


def test_security_and_auth_middleware_present():
    required = {
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.security.SecurityMiddleware",
    }
    installed = set(settings.MIDDLEWARE or [])
    missing = [m for m in required if m not in installed]
    assert not missing, f"Missing essential middleware: {missing}"


def test_static_and_media_settings_are_valid():
    assert hasattr(settings, "STATIC_URL") and settings.STATIC_URL.startswith("/"), "STATIC_URL must start with '/'"
    if getattr(settings, "MEDIA_URL", None):
        assert settings.MEDIA_URL.startswith("/"), "MEDIA_URL must start with '/'"
    if hasattr(settings, "STATICFILES_DIRS"):
        for p in settings.STATICFILES_DIRS:
            assert isinstance(p, (str, os.PathLike)) and os.path.exists(p), f"STATICFILES_DIR not found: {p}"


@pytest.mark.skipif(
    not any(str(p).endswith("manifest.json") for p in getattr(settings, "STATICFILES_DIRS", [])) and
    not os.path.exists(os.path.join(getattr(settings, "BASE_DIR", os.getcwd()), "static", "manifest.json")),
    reason="PWA manifest.json not present; skipping optional check.",
)
def test_pwa_manifest_exists_when_configured():
    candidates = []
    for p in getattr(settings, "STATICFILES_DIRS", []):
        candidates.append(os.path.join(p, "manifest.json"))
    candidates.append(os.path.join(getattr(settings, "BASE_DIR", os.getcwd()), "static", "manifest.json"))
    assert any(os.path.exists(c) for c in candidates), "manifest.json was expected but not found"
