# core/utils/archive.py
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.files.storage import FileSystemStorage


def archive_file(file_obj: Any, folder: str = "general") -> str:
    """
    أرشفة ملف داخل MEDIA_ROOT/archives/<folder>
    وإرجاع الـ URL النهائي له.
    """
    base_dir = Path(settings.MEDIA_ROOT) / "archives" / folder
    base_dir.mkdir(parents=True, exist_ok=True)

    fs = FileSystemStorage(location=str(base_dir))
    filename = fs.save(getattr(file_obj, "name", "uploaded_file"), file_obj)
    return fs.url(filename)
