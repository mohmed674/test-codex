from __future__ import annotations

import logging
import os
import tempfile
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Final

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST

from .speech_to_text import (SpeechEngineUnavailable, TranscriptionError,
                             stt_available, transcribe_audio)

logger = logging.getLogger(__name__)

# قيود أمان للرفع
_ALLOWED_CONTENT_TYPES: Final[set[str]] = {
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/ogg",
    "audio/x-ogg",
    "audio/webm",
    "audio/mp4",
    "video/mp4",  # أحيانًا الصوت يجي mp4
    "application/octet-stream",  # بعض المتصفحات
}
_MAX_UPLOAD_MB: Final[int] = int(getattr(settings, "VOICE_MAX_UPLOAD_MB", 25))
_MAX_UPLOAD_BYTES: Final[int] = _MAX_UPLOAD_MB * 1024 * 1024


def _safe_media_root() -> Path:
    """
    أرجع مسار صالح من نوع Path لا يقبل None — لتفادي خطأ mypy:
    settings.MEDIA_ROOT ممكن يكون None في بعض البيئات، فنستخدم tmp بديلًا.
    """
    media_root = getattr(settings, "MEDIA_ROOT", None)
    if not media_root:
        return Path(tempfile.gettempdir())
    # لو كان str → حوله Path. لو كان Path بالفعل → ارجعه كما هو.
    return media_root if isinstance(media_root, Path) else Path(str(media_root))


# اختيار مسار مؤقّت آمن داخل MEDIA لو متاح
_TMP_DIR = _safe_media_root() / "voice_tmp"
_TMP_DIR.mkdir(parents=True, exist_ok=True)


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"ok": False, "error": message}, status=status)


@require_POST
def upload_voice(request: HttpRequest) -> HttpResponse:
    """
    يرفع ملف صوتي (أو فيديو قصير) ويعيد نص مُفرّغ STT.
    """
    f = request.FILES.get("file")
    if not f:
        return _json_error(_("No file uploaded."), status=400)

    # فحص النوع والحجم
    ctype = (f.content_type or "").lower()
    if ctype not in _ALLOWED_CONTENT_TYPES:
        logger.warning("Blocked content_type=%s name=%s", ctype, f.name)
        return _json_error(_("Unsupported content type."), status=415)

    if f.size and f.size > _MAX_UPLOAD_BYTES:
        return _json_error(
            _(f"File too large. Max allowed is {_MAX_UPLOAD_MB} MB."),
            status=413,
        )

    # باراميترات اختيارية
    language = (request.POST.get("language") or "").strip() or getattr(
        settings, "STT_DEFAULT_LOCALE", "ar-EG"
    )
    prefer_offline = (request.POST.get("prefer_offline") or "").lower() in {
        "1",
        "true",
        "yes",
    }

    # حفظ مؤقت آمن
    suffix = Path(f.name).suffix or ".bin"
    with tempfile.NamedTemporaryFile(dir=_TMP_DIR, suffix=suffix, delete=False) as tmp:
        for chunk in f.chunks():
            tmp.write(chunk)
        tmp_path = Path(tmp.name)

    try:
        text = transcribe_audio(
            tmp_path, language=language, prefer_offline=prefer_offline
        ).strip()
        logger.info(
            "voice_upload: lang=%s offline=%s len=%d file=%s",
            language,
            prefer_offline,
            len(text),
            tmp_path.name,
        )
        return JsonResponse(
            {
                "ok": True,
                "text": text,
                "meta": {
                    "language": language,
                    "backend_offline_preferred": prefer_offline,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
            },
            status=200,
        )
    except SpeechEngineUnavailable as e:
        logger.warning("STT unavailable: %s", e)
        return _json_error(
            _(
                "Speech-to-text backend is unavailable. "
                "Install/enable online SR or configure offline Vosk model."
            ),
            status=503,
        )
    except TranscriptionError:
        logger.exception("Transcription error for %s", tmp_path)
        return _json_error(_("Failed to process audio."), status=422)
    except Exception:
        logger.exception("Unexpected error while transcribing %s", tmp_path)
        return _json_error(_("Unexpected server error."), status=500)
    finally:
        with suppress(Exception):
            tmp_path.unlink(missing_ok=True)


@require_GET
def stt_status(request: HttpRequest) -> HttpResponse:
    """
    فحص سريع لحالة محركات STT (لا يستدعي أي API خارجي).
    """
    available = stt_available()
    has_vosk_dir = bool(os.environ.get("VOSK_MODEL_DIR", "").strip())
    return JsonResponse(
        {
            "ok": True,
            "available": available,
            "vosk_model_configured": has_vosk_dir,
            "default_locale": getattr(settings, "STT_DEFAULT_LOCALE", "ar-EG"),
        },
        status=200,
    )


@require_GET
def voice_logs(request: HttpRequest) -> HttpResponse:
    """
    Placeholder لسجلات وحدة الصوت.
    """
    return JsonResponse(
        {
            "ok": True,
            "message": _("Voice module is active."),
            "now": datetime.utcnow().isoformat() + "Z",
        },
        status=200,
    )
