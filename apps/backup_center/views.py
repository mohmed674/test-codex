from __future__ import annotations

import logging
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

# نستورد الموديول ثم نستخدمه داخل _enqueue لتفادي مشاكل typing مع .delay()
from . import tasks

logger = logging.getLogger(__name__)


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"ok": False, "error": message}, status=status)


def _is_superuser(user: Any) -> bool:
    """فحص آمن للتايبنج: يتعامل مع AnonymousUser و User."""
    return bool(getattr(user, "is_superuser", False))


def _enqueue(task_obj: Any) -> Any:
    """
    استدعاء آمن لتاسك Celery بدون صدام مع أنظمة الـ typing/IDE:
    - يجرّب delay()
    - ثم apply_async()
    - يرمي RuntimeError لو مفيش ولا واحدة
    """
    d = getattr(task_obj, "delay", None)
    if callable(d):
        return d()
    a = getattr(task_obj, "apply_async", None)
    if callable(a):
        return a()
    raise RuntimeError("Invalid Celery task object: no delay/apply_async found")


@require_POST
def create_database_backup_view(request: HttpRequest) -> HttpResponse:
    """
    يشغّل تاسك نسخ قاعدة البيانات (Celery).
    - 401 لو غير مسجّل
    - 403 لو ليس مشرفًا
    - 405 لو الميثود ليست POST
    """
    if request.method != "POST":
        return _json_error(_("Method not allowed."), status=405)

    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return _json_error(_("Authentication required."), status=401)

    if not _is_superuser(user):
        return _json_error(_("Administrator privileges required."), status=403)

    try:
        task = _enqueue(tasks.auto_backup_database)
        logger.info("DB backup task enqueued: %s", getattr(task, "id", None))
        return JsonResponse(
            {
                "ok": True,
                "task_id": getattr(task, "id", None),
                "message": _("Database backup started."),
            },
            status=202,
        )
    except Exception:
        logger.exception("Failed to enqueue DB backup task")
        return _json_error(_("Failed to enqueue database backup."), status=500)


@require_POST
def create_media_backup_view(request: HttpRequest) -> HttpResponse:
    """
    يشغّل تاسك أرشفة MEDIA (Celery).
    """
    if request.method != "POST":
        return _json_error(_("Method not allowed."), status=405)

    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return _json_error(_("Authentication required."), status=401)

    if not _is_superuser(user):
        return _json_error(_("Administrator privileges required."), status=403)

    try:
        task = _enqueue(tasks.backup_media)
        logger.info("Media backup task enqueued: %s", getattr(task, "id", None))
        return JsonResponse(
            {
                "ok": True,
                "task_id": getattr(task, "id", None),
                "message": _("Media backup started."),
            },
            status=202,
        )
    except Exception:
        logger.exception("Failed to enqueue media backup task")
        return _json_error(_("Failed to enqueue media backup."), status=500)
