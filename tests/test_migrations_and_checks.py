# tests/test_migrations_and_checks.py

import pytest
from django.core.management import call_command
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db(transaction=True)


def test_system_checks_ok():
    call_command("check", fail_level="ERROR", verbosity=0)


def test_no_missing_migrations():
    try:
        call_command("makemigrations", check=True, dry_run=True, verbosity=0)
    except SystemExit as e:
        pytest.fail(f"Missing migrations detected (makemigrations --check): exit code {e.code}")


def test_all_migrations_applied():
    connection = connections["default"]
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    assert not plan, f"Unapplied migrations: {[f'{m.app_label}.{m.name}' for m, _ in plan]}"


def test_auth_user_table_exists():
    connection = connections["default"]
    User = get_user_model()
    table_name = User._meta.db_table
    existing = set(connection.introspection.table_names())
    assert table_name in existing, f"Missing auth table {table_name}"
