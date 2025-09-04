# apps/internal_monitoring/admin.py
from contextlib import suppress
from django.apps import apps as dj_apps
from django.contrib import admin

try:
    from django.contrib.admin.sites import AlreadyRegistered  # type: ignore[attr-defined]
except Exception:
    class AlreadyRegistered(Exception):
        """Fallback لو ما اتعرفتش AlreadyRegistered (stubs)."""

# النماذج اللي نحاول نسجلها (قد لا تكون كلها موجودة)
_MODEL_NAMES = (
    "InventoryDiscrepancy",
    "SuspiciousActivity",
    "RiskIncident",
    "ReportLog",
    "DisciplinaryAction",
)

for _name in _MODEL_NAMES:
    model = dj_apps.get_model("internal_monitoring", _name, require_ready=False)
    if model is not None:
        with suppress(AlreadyRegistered):
            admin.site.register(model)
