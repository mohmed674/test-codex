# ERP_CORE/ERP_CORE/celery_app.py
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"⏱️ Celery يعمل: Task Request: {self.request!r}")


# دمج جدول Beat القادم من settings مع مهام النسخ الاحتياطي هنا
_merged = dict(getattr(settings, "CELERY_BEAT_SCHEDULE", {}) or {})

_backup_schedule = {
    "daily-db-backup": {
        "task": "backup_center.tasks.auto_backup_database",
        "schedule": crontab(hour=2, minute=0),
    },
    "daily-media-backup": {
        "task": "backup_center.tasks.auto_backup_media",
        "schedule": crontab(hour=2, minute=30),
    },
}

_merged.update(_backup_schedule)
app.conf.beat_schedule = _merged
