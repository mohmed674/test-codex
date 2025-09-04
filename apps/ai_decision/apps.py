# PATH: D:\ERP_CORE\ai_decision\apps.py
from __future__ import annotations

from contextlib import suppress

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AiDecisionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ai_decision"
    label = "ai_decision"
    verbose_name = _("الذكاء الاصطناعي (Copilot)")

    def ready(self) -> None:
        """Import app signals if present (safe, no hard failure)."""
        with suppress(Exception):
            from . import signals  # noqa: F401
