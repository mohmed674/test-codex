# config/__init__.py
from __future__ import annotations

from typing import TYPE_CHECKING

# ملاحظة:
# - أثناء تشغيل mypy (والـ django-stubs plugin)، بنمنع أي import جانبي
#   عشان ما يحملش celery أو أكواد bootstrapping.
# - وقت التشغيل العادي (Django/Celery) هنعمل import النسبي الصحيح.

if not TYPE_CHECKING:
    try:
        # استيراد نسبي صحيح داخل باكدچ config
        from .celery_app import app as celery_app  # noqa: F401
    except Exception:
        # في بيئات الفحص أو بدون celery: نتجاهل بهدوء
        celery_app = None  # type: ignore[assignment]
