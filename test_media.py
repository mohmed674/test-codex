import pytest
from django.apps import apps
from django.db import connection
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_media_tables_exist_after_migrate():
    """
    التحقق من وجود جداول media بعد الميجريشن.
    """
    existing = set(connection.introspection.table_names())
    expected = {
        "media_file",      # مثال: جدول الملفات
        "media_folder",    # مثال: جدول المجلدات
    }
    missing = [t for t in expected if t not in existing]
    assert not missing, f"Media tables missing: {missing}"


def test_media_app_is_installed():
    """
    التأكد من أن تطبيق media مُسجّل في INSTALLED_APPS.
    """
    installed = {cfg.name for cfg in apps.get_app_configs()}
    assert "media" in installed, "media app is not installed"


@pytest.mark.django_db
def test_create_media_file_with_user():
    """
    تجربة إنشاء كائن MediaFile وربطه بـ AUTH_USER_MODEL.
    """
    User = get_user_model()
    MediaFile = apps.get_model("media", "File")

    user = User.objects.create_user(username="tester", password="secret123")
    media_file = MediaFile.objects.create(
        name="test_file.png",
        uploaded_by=user
    )

    assert MediaFile.objects.count() == 1
    assert media_file.uploaded_by.username == "tester"
