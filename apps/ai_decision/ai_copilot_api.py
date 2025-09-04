"""AI Copilot API layer.

- Exposes `query_openai(query: str) -> str` used by views.py.
- Provider-agnostic: uses settings.AI_COPILOT_PROVIDER ("OPENAI" / "DUMMY").
- Safe defaults: if no API key or provider disabled, falls back to deterministic reply.
- No secrets hardcoded. Timeouts + error handling included.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

import requests
from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

# ---- Configuration helpers -------------------------------------------------


def _get_provider() -> str:
    # default to DUMMY to avoid runtime failures in dev/test
    return getattr(settings, "AI_COPILOT_PROVIDER", "DUMMY").upper()


def _get_model() -> str:
    # safe default, can be overridden in settings
    return getattr(settings, "AI_COPILOT_MODEL", "gpt-4o-mini")


def _get_openai_key() -> str | None:
    # prefer Django settings, then env variable
    key = getattr(settings, "OPENAI_API_KEY", None)
    if key:
        return key
    return os.environ.get("OPENAI_API_KEY")


# ---- Public API ------------------------------------------------------------


def query_openai(query: str) -> str:
    """Return an assistant reply for the user's `query`.

    Chooses backend by settings:
      - AI_COPILOT_PROVIDER="OPENAI": call OpenAI Chat Completions API
      - otherwise: return a deterministic, safe local reply.

    Always returns a string (never raises).
    """
    q = (query or "").strip()
    if not q:
        return _("يرجى كتابة سؤال واضح لأتمكن من المساعدة.")

    provider = _get_provider()
    try:
        if provider == "OPENAI":
            key = _get_openai_key()
            if not key:
                logger.warning("OPENAI provider selected but no API key configured.")
                return _fallback_reply(q)

            return _openai_chat_completion(q, key, _get_model())
        # Future: add "AZURE_OPENAI", "ANYSCALE", ...
        return _fallback_reply(q)
    except Exception as exc:  # noqa: BLE001
        # We must never break the UI; log and fallback.
        logger.exception("Copilot query failed: %s", exc)
        return _fallback_reply(q)


# ---- Providers -------------------------------------------------------------


def _openai_chat_completion(query: str, api_key: str, model: str) -> str:
    """Call OpenAI Chat Completions with strict timeouts and minimal payload."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "You are an ERP AI copilot. Answer concisely and factually. "
        "If data is unknown, say so. Keep answers suitable for a business user."
    )

    payload: Dict[str, Any] = {
        "model": model,
        "temperature": 0.2,
        "max_tokens": 512,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
    }

    resp = requests.post(
        url,
        headers=headers,
        data=json.dumps(payload),
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    # Defensive extraction
    choice = (
        (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
    )
    return choice or _fallback_reply(query)


def _fallback_reply(query: str) -> str:
    """Deterministic, safe local response when LLM is unavailable."""
    lowered = query.lower()
    if "سعر" in lowered or "price" in lowered:
        return _(
            "لا أمتلك حالياً بيانات الأسعار المباشرة. " "جرّب طلب تقرير المبيعات المحلي."
        )
    if "مبيعات" in lowered or "sales" in lowered:
        return _("يمكنني تلخيص تقارير المبيعات إذا زودتني " "بنطاق التاريخ أو المصدر.")
    return _(
        "تم استلام سؤالك. لتفاصيل أدق، حدّد نطاق البيانات "
        "أو استخدم الكلمات المفتاحية."
    )


# ---- Minimal HTTP endpoints (optional) -------------------------------------


@require_http_methods(["GET"])
def healthcheck(_request):
    """Lightweight readiness probe."""
    return JsonResponse({"ok": True, "provider": _get_provider()})


@require_http_methods(["POST"])
def copilot_api(request):
    """JSON endpoint: {query: string} -> {reply: string}."""
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:  # noqa: BLE001
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    query = (body.get("query") or "").strip()
    reply = query_openai(query)
    return JsonResponse({"reply": reply})
