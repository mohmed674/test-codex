# apps/asset_lifecycle/admin.py
from __future__ import annotations

from contextlib import suppress
from typing import Type

from django.apps import apps
from django.contrib import admin
from django.db.models import Model


def _register_all_models(app_label: str) -> None:
    """
    Register all models in the given app with the Django admin site.

    - Avoids wildcard imports (fixes F403/F405).
    - Uses contextlib.suppress to ignore AlreadyRegistered (SIM105).
    """
    app_config = apps.get_app_config(app_label)
    for model in app_config.get_models():  # type: ignore[assignment]
        m: Type[Model] = model
        with suppress(admin.sites.AlreadyRegistered):
            admin.site.register(m)


# Register all models of this app.
_register_all_models("asset_lifecycle")
