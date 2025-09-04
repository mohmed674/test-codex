"""Admin registrations for ai_decision app."""

from __future__ import annotations

from contextlib import suppress

from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from apps.ai_decision.models import (AIDecisionAlert, AIDecisionLog,
                                     DecisionAnalysis)


def _safe_register(model) -> None:
    """Register model in admin if not already registered."""
    with suppress(AlreadyRegistered):
        admin.site.register(model)


_safe_register(AIDecisionAlert)
_safe_register(DecisionAnalysis)
_safe_register(AIDecisionLog)
