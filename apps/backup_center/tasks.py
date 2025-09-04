"""
Secure backup tasks for ERP:
- Database JSON dump via Django's call_command (no shell).
- Media archive via shutil (no shell).
- Optional upload_to_drive() if available.

Compliant with bandit (no B605), flake8, mypy.
"""

from __future__ import annotations

import logging
import shutil
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from celery import shared_task
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

logger = logging.getLogger(__name__)

# ---- Constants ----------------------------------------------------------------
_BACKUPS_ROOT: Final[Path] = Path(
    getattr(settings, "BACKUPS_ROOT", settings.BASE_DIR / "backups")
)
_DB_DIR: Final[Path] = _BACKUPS_ROOT / "db"
_MEDIA_DIR: Final[Path] = _BACKUPS_ROOT / "media"
_EXCLUDES: Final[list[str]] = [
    "auth.permission",
    "contenttypes",
]  # same behavior as CLI example


# ---- Optional integrations ----------------------------------------------------
def _maybe_upload_to_drive(file_path: Path, kind: str) -> None:
    """
    Call optional upload_to_drive(file_path, kind) if available.
    Does nothing when the integration is absent.
    """
    with suppress(Exception):
        from .utils import upload_to_drive  # type: ignore

        upload_to_drive(str(file_path), kind)
        logger.info("Uploaded %s to drive: %s", kind, file_path.name)


# ---- Optional persistence model ----------------------------------------------
@dataclass(slots=True, frozen=True)
class _BackupMeta:
    kind: str  # "db" or "media"
    path: Path


def _save_record(meta: _BackupMeta) -> None:
    """
    Create BackupRecord if model exists; otherwise skip silently.
    """
    with suppress(Exception):
        from .models import BackupRecord  # type: ignore

        BackupRecord.objects.create(kind=meta.kind, path=str(meta.path))
        logger.info("BackupRecord saved: %s -> %s", meta.kind, meta.path.name)


# ---- Helpers ------------------------------------------------------------------
def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _ts() -> str:
    return timezone.now().strftime("%Y%m%d_%H%M%S")


# ---- Public tasks -------------------------------------------------------------
@shared_task(name="backup_center.auto_backup_database")
def auto_backup_database() -> str:
    """
    Create a JSON dump of the database with natural keys, no shell invocation.
    Returns the created file path (string).
    """
    _ensure_dir(_DB_DIR)
    out_file = _DB_DIR / f"db_{_ts()}.json"

    # Use Django management command directly -> safe & portable
    with out_file.open("w", encoding="utf-8") as fh:
        call_command(
            "dumpdata",
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True,
            exclude=_EXCLUDES,
            indent=2,
            stdout=fh,
        )

    meta = _BackupMeta(kind="db", path=out_file)
    _save_record(meta)
    _maybe_upload_to_drive(out_file, kind="db")
    logger.info("Database backup created: %s", out_file.as_posix())
    return out_file.as_posix()


@shared_task(name="backup_center.backup_media")
def backup_media() -> str:
    """
    Create a ZIP archive of MEDIA_ROOT using shutil.make_archive (no shell).
    Returns the created archive path (string).
    """
    if not getattr(settings, "MEDIA_ROOT", None):
        msg = "MEDIA_ROOT is not configured; skipping media backup."
        logger.warning(msg)
        return msg

    _ensure_dir(_MEDIA_DIR)
    base_name = _MEDIA_DIR / f"media_{_ts()}"
    archive_path = shutil.make_archive(
        base_name=str(base_name),
        format="zip",
        root_dir=str(Path(settings.MEDIA_ROOT)),
    )

    archive_file = Path(archive_path)
    meta = _BackupMeta(kind="media", path=archive_file)
    _save_record(meta)
    _maybe_upload_to_drive(archive_file, kind="media")
    logger.info("Media backup created: %s", archive_file.as_posix())
    return archive_file.as_posix()


# ---- Backward-compat aliases (للتوافق مع أي كود قديم يستدعي أسماء مختلفة) ----
# أي استدعاء قديم لـ create_database_backup / create_media_backup سيستمر بالعمل:
create_database_backup = auto_backup_database
create_media_backup = backup_media
