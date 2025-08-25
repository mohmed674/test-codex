import importlib
import os
from typing import Iterable, Set, List

import pytest
from django.apps import apps
from django.conf import settings
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from django.test import Client
from django.urls import get_resolver, set_urlconf

EXPECTED_LABELS: Set[str] = {"employees", "employee_monitoring", "survey", "media"}

def _existing_tables() -> Set[str]:
    return set(connection.introspection.table_names())

def _models_for_labels(labels: Iterable[str]):
    for label in labels:
        try:
            for model in apps.get_app_config(label).get_models():
                yield label, model
        except LookupError:
            continue

def test_expected_apps_are_installed():
    installed_labels = {cfg.label for cfg in apps.get_app_configs()}
    missing = sorted(lbl for lbl in EXPECTED_LABELS if lbl not in installed_labels)
    assert not missing, f"Expected app labels not installed: {missing}"

@pytest.mark.django_db
def test_migration_graph_loads_without_missing_nodes():
    loader = MigrationLoader(connection)
    graph = loader.graph
    assert len(graph.nodes) > 0

@pytest.mark.django_db
def test_expected_apps_have_applied_migrations():
    loader = MigrationLoader(connection)
    applied_labels = {name[0] for name in loader.applied_migrations}
    graph_labels = {name[0] for name in loader.graph.nodes}
    missing_any: List[str] = []
    for label in EXPECTED_LABELS:
        if label not in graph_labels:
            continue  # not defined in graph at كل
        if label not in applied_labels:
            missing_any.append(label)
    assert not missing_any, f"Apps have no applied migrations: {missing_any}"

@pytest.mark.django_db
def test_all_models_tables_exist_for_expected_apps():
    existing = _existing_tables()
    missing_tables = []
    for label, model in _models_for_labels(EXPECTED_LABELS):
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

@pytest.mark.django_db
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
            assert hasattr(p, "__fspath__") or isinstance(p, (str, os.PathLike)), f"Bad STATICFILES_DIR entry: {p}"

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
