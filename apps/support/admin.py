from contextlib import suppress
from typing import TYPE_CHECKING

from django.contrib import admin

# بعض إصدارات stubs لا تُعرّف AlreadyRegistered صراحةً؛ نوحّد الاستيراد مع fallback
try:
    from django.contrib.admin.sites import AlreadyRegistered  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    class AlreadyRegistered(Exception):  # type: ignore[unused-ignore]
        """Fallback for static analyzers when symbol isn't exposed."""

# لتفادي تحذير Pylance "unknown attribute of module" مع import module
# نعرّف الأنواع لأغراض الفحص فقط (لا تُنفّذ وقت التشغيل)
if TYPE_CHECKING:  # pragma: no cover
    from apps.support.models import SupportResponse as _SupportResponse
    from apps.support.models import SupportTicket as _SupportTicket

# نحمّل الموديلات عبر الموديول ثم نتحقق من وجود الصفات وقت التشغيل
from apps.support import models as support_models

SupportTicket = getattr(support_models, "SupportTicket", None)
SupportResponse = getattr(support_models, "SupportResponse", None)

# ✅ تسجيل آمن Idempotent
if SupportTicket is not None:
    with suppress(AlreadyRegistered):
        admin.site.register(SupportTicket)

if SupportResponse is not None:
    with suppress(AlreadyRegistered):
        admin.site.register(SupportResponse)
