import os
import datetime
from django.conf import settings
from .models import BackupRecord
from celery import shared_task
from .utils.drive_uploader import upload_to_drive


@shared_task
def auto_backup_database():
    """
    ✅ يقوم بعمل نسخة احتياطية من قاعدة البيانات بصيغة JSON
    ويتم تخزينها في مجلد backups داخل مجلد المشروع،
    ثم يرفعها إلى Google Drive ويسجلها في قاعدة البيانات.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
import os
import datetime
from django.conf import settings
from apps.backup_center.models import BackupRecord
from celery import shared_task
from apps.backup_center.utils.drive_uploader import upload_to_drive  # ✅ استيراد مطلق بدون تحذير


@shared_task
def auto_backup_database():
    """
    ✅ يقوم بعمل نسخة احتياطية من قاعدة البيانات بصيغة JSON
    ويتم تخزينها في مجلد backups داخل مجلد المشروع،
    ثم يرفعها إلى Google Drive ويسجلها في قاعدة البيانات.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    path = os.path.join(settings.BASE_DIR, "backups")
    os.makedirs(path, exist_ok=True)
    filename = f"db_auto_backup_{timestamp}.json"
    filepath = os.path.join(path, filename)

    os.system(
        f"python manage.py dumpdata --natural-foreign --natural-primary "
        f"--exclude auth.permission --exclude contenttypes > {filepath}"
    )

    BackupRecord.objects.create(file_path=filepath, file_type="database")
    upload_to_drive(filepath)


@shared_task
def auto_backup_media():
    """
    ✅ يقوم بضغط مجلد media بالكامل في ملف ZIP وتخزينه في مجلد backups،
    ثم يرفع النسخة إلى Google Drive ويسجلها في قاعدة البيانات.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    path = os.path.join(settings.BASE_DIR, "backups")
    os.makedirs(path, exist_ok=True)
    filename = f"media_auto_backup_{timestamp}.zip"
    filepath = os.path.join(path, filename)

    os.system(f"zip -r {filepath} {settings.MEDIA_ROOT}")

    BackupRecord.objects.create(file_path=filepath, file_type="media")
    upload_to_drive(filepath)


# 🟡 دعم النسخ اليدوي (اختياري من لوحة الإدارة أو من زر)
def create_database_backup():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"db_backup_{timestamp}.json"
    path = os.path.join(settings.BASE_DIR, "backups", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    os.system(
        f"python manage.py dumpdata --natural-foreign --natural-primary "
        f"--exclude auth.permission --exclude contenttypes > {path}"
    )

    BackupRecord.objects.create(file_path=path, file_type="database")


def create_media_backup():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    archive_name = f"media_backup_{timestamp}.zip"
    archive_path = os.path.join(settings.BASE_DIR, "backups", archive_name)
    os.makedirs(os.path.dirname(archive_path), exist_ok=True)

    os.system(f"zip -r {archive_path} {settings.MEDIA_ROOT}")

    BackupRecord.objects.create(file_path=archive_path, file_type="media")
