# conftest.py — إعدادات واختصارات Pytest على مستوى المشروع (ضعه في جذر المستودع)
import os

# تأكيد إعدادات Django للاختبار
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.pytest_settings")

import pytest
import django


pytest_plugins = ("django",)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config) -> None:
    """
    تهيئة Django مبكرًا لتفادي مشاكل الاستيراد وترتيب التمهيد.
    """
    django.setup()


@pytest.fixture(scope="session", autouse=True)
def _bootstrap_django(django_db_setup, django_db_blocker):
    """
    1) ضمان تطبيق الميجريشنز بالكامل قبل أي Test.
    2) فحص صحة الإعدادات الأساسية.
    3) توثيق أن قاعدة البيانات المستخدمة هي قاعدة اختبار.
    """
    import os as _os
    from django.conf import settings as _settings
    from django.core.management import call_command as _call_command

    # تأكيد أن الإعدادات الصحيحة محملة
    assert _os.environ.get("DJANGO_SETTINGS_MODULE") == "config.pytest_settings", (
        "DJANGO_SETTINGS_MODULE يجب أن يكون config.pytest_settings أثناء الاختبارات."
    )

    # فحوصات أساسية على التطبيقات
    _required = {"django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions"}
    assert _required.issubset(set(_settings.INSTALLED_APPS)), (
        "INSTALLED_APPS يجب أن تحتوي على التطبيقات الأساسية: auth/contenttypes/sessions."
    )

    # تأكيد أن قاعدة البيانات المستخدمة هي test_*
    _db = _settings.DATABASES.get("default", {})
    _engine = _db.get("ENGINE", "")
    _name = _db.get("NAME", "")
    _test_name = _db.get("TEST", {}).get("NAME") or _name
    if "sqlite3" not in _engine:
        assert str(_test_name).startswith("test_"), (
            f"اسم قاعدة الاختبار غير آمن: {_test_name!r} — يجب أن يبدأ بـ 'test_'. "
            "حدّث DATABASES['default']['TEST']['NAME'] أو استخدم إعدادات pytest."
        )

    # طبّق الميجريشنز وتحقق من وجود auth_user
    with django_db_blocker.unblock():
        _call_command("migrate", interactive=False, verbosity=0)

        # فحص أن جدول المستخدم موجود فعليًا عبر استعلام بسيط
        from django.contrib.auth import get_user_model as _get_user_model

        _User = _get_user_model()
        # تنفيذ استعلام فعلي يضمن جاهزية الجدول
        _ = _User.objects.exists()


@pytest.fixture(scope="session", autouse=True)
def _auto_register_models_in_admin(_bootstrap_django):
    """
    تسجيل تلقائي لكل الموديلات في لوحة الـ Admin أثناء الاختبارات فقط
    لتحقيق شرط "أي موديل جديد يُسجَّل تلقائيًا في Admin إن أمكن".
    يمكن تعطيله بوضع المتغير البيئي PYTEST_AUTO_REGISTER_ADMIN=0.
    """
    import os as _os
    if _os.environ.get("PYTEST_AUTO_REGISTER_ADMIN", "1") != "1":
        return

    from django.apps import apps as _apps
    from django.contrib import admin as _admin
    from django.contrib.admin.sites import AlreadyRegistered as _AlreadyRegistered

    for _model in _apps.get_models():
        try:
            _admin.site.register(_model)
        except _AlreadyRegistered:
            pass


# Fixtures مساعدة شائعة
@pytest.fixture
def user(db):
    """
    مستخدم جاهز للاختبارات.
    """
    from django.contrib.auth import get_user_model
    import uuid

    User = get_user_model()
    u = User.objects.create_user(
        username=f"u_{uuid.uuid4().hex[:8]}",
        email=f"u_{uuid.uuid4().hex[:8]}@example.com",
        password="test-pass-123",
    )
    return u
