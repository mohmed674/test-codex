"""
Speech-to-Text utilities for voice commands.

- Lazy imports (لا نكسر check --deploy).
- يعمل مع ملفات صوتية مرفوعة (بدون ميكروفون).
- تطبيع الصوت إلى WAV 16kHz Mono قبل التعرف.
- STT أونلاين (Google عبر SpeechRecognition) مع فولباك أوفلاين (Vosk) عند توافره.
- Typing واضح، استثناءات نظيفة، i18n للرسائل، تسجيل آمن بدون أسرار.

DoD: black/isort/flake8/mypy/bandit clean.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Optional

from django.conf import settings
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

# ---- Constants ----------------------------------------------------------------
_DEFAULT_LANG: Final[str] = getattr(settings, "LANGUAGE_CODE", "ar")
_STT_DEFAULT_LOCALE: Final[str] = getattr(settings, "STT_DEFAULT_LOCALE", "ar-EG")
_VOSK_MODEL_DIR_ENV: Final[str] = "VOSK_MODEL_DIR"


# ---- Exceptions ---------------------------------------------------------------
class SpeechEngineUnavailable(Exception):
    """Raised when a required speech backend is missing or misconfigured."""


class TranscriptionError(Exception):
    """Raised when transcription fails for a non-recoverable reason."""


# ---- Result DTO ---------------------------------------------------------------
@dataclass(slots=True, frozen=True)
class TranscriptionResult:
    text: str
    backend: str  # "google" | "vosk"
    language: str


# ---- Helpers ------------------------------------------------------------------
def _normalize_to_wav16k_mono(src_path: Path) -> Path:
    """
    Convert any audio file to 16kHz mono WAV using pydub/ffmpeg.
    Returns path to the normalized temporary WAV file next to the source.
    """
    try:
        from pydub import AudioSegment  # lazy
        from pydub.utils import which
    except Exception as exc:  # pragma: no cover
        raise SpeechEngineUnavailable(
            _("Audio processing backend is unavailable (pydub).")
        ) from exc

    try:
        AudioSegment.converter = which("ffmpeg") or AudioSegment.converter
    except Exception:
        # سيُخطئ عند التصدير إن لم يكن ffmpeg متاحًا
        pass

    dst_path = src_path.with_suffix(".normalized.wav")
    try:
        audio = AudioSegment.from_file(src_path.as_posix())
        audio = audio.set_channels(1).set_frame_rate(16_000).set_sample_width(2)
        audio.export(dst_path.as_posix(), format="wav")
        return dst_path
    except Exception as exc:
        logger.exception("Audio normalization failed for %s", src_path)
        raise TranscriptionError(_("Failed to normalize audio.")) from exc


def _try_google_sr(wav_path: Path, language: str) -> Optional[TranscriptionResult]:
    """
    Try online SpeechRecognition (Google Web Speech API).
    Returns TranscriptionResult or None if backend not available or request failed.
    """
    try:
        import speech_recognition as sr  # lazy
    except Exception:
        return None

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path.as_posix()) as source:
            audio = recognizer.record(source)
    except Exception as exc:
        logger.exception("Reading WAV failed for SR: %s", wav_path)
        raise TranscriptionError(_("Failed to read normalized audio.")) from exc

    from typing import Callable
    from typing import Optional as TypingOptional

    google_recognize: TypingOptional[Callable[..., str]] = getattr(
        recognizer, "recognize_google", None
    )
    if not callable(google_recognize):
        logger.warning("SpeechRecognition missing 'recognize_google' method.")
        return None

    try:
        text = google_recognize(audio, language=language) or ""
        return TranscriptionResult(text=text, backend="google", language=language)
    except Exception as exc:
        try:
            if isinstance(exc, sr.UnknownValueError):  # type: ignore[attr-defined]
                return TranscriptionResult(text="", backend="google", language=language)
            if isinstance(exc, sr.RequestError):  # type: ignore[attr-defined]
                logger.warning("Google STT request error: %s", exc)
                return None
        except Exception:
            logger.warning("Google STT error: %s", exc)
            return None
        return None


def _try_vosk_offline(wav_path: Path, language: str) -> Optional[TranscriptionResult]:
    """
    Try offline STT via Vosk if installed and model is present.
    Returns TranscriptionResult or None if not available.
    """
    try:
        import json
        import os
        import wave

        import vosk
    except Exception:
        return None

    model_dir = os.environ.get(_VOSK_MODEL_DIR_ENV, "").strip()
    if not model_dir:
        logger.info("Vosk model dir not configured via %s.", _VOSK_MODEL_DIR_ENV)
        return None

    try:
        model = vosk.Model(model_dir)
        with wave.open(wav_path.as_posix(), "rb") as wf:
            rec = vosk.KaldiRecognizer(model, wf.getframerate())
            parts: list[str] = []
            while True:
                data = wf.readframes(4000)
                if not data:
                    break
                if rec.AcceptWaveform(data):
                    try:
                        parts.append(json.loads(rec.Result()).get("text", ""))
                    except Exception:
                        pass
            try:
                parts.append(json.loads(rec.FinalResult()).get("text", ""))
            except Exception:
                pass
        text = " ".join(p for p in parts if p).strip()
        return TranscriptionResult(text=text, backend="vosk", language=language)
    except Exception as exc:
        logger.warning("Vosk offline STT failed: %s", exc)
        return None


# ---- Public API ---------------------------------------------------------------
def transcribe_audio(
    file_path: str | Path,
    *,
    language: Optional[str] = None,
    prefer_offline: bool = False,
) -> str:
    """
    Transcribe an audio file to text.
    """
    src = Path(file_path)
    if not src.exists() or not src.is_file():
        raise TranscriptionError(_("Audio file does not exist."))

    lang = (language or _STT_DEFAULT_LOCALE or _DEFAULT_LANG).strip()
    wav = _normalize_to_wav16k_mono(src)

    backends = (
        (_try_vosk_offline, _try_google_sr)
        if prefer_offline
        else (_try_google_sr, _try_vosk_offline)
    )
    for backend in backends:
        res = backend(wav, lang)
        if isinstance(res, TranscriptionResult):
            logger.info(
                "STT backend=%s lang=%s len=%d",
                res.backend,
                res.language,
                len(res.text),
            )
            return res.text

    raise SpeechEngineUnavailable(
        _(
            "No speech-to-text backend available. Install and configure "
            "'SpeechRecognition' (online) or set VOSK_MODEL_DIR for offline."
        )
    )


def stt_available() -> bool:
    """
    Quick check to see if at least one backend is importable/configured.
    """
    try:
        import speech_recognition  # noqa: F401

        return True
    except Exception:
        pass
    try:
        import os  # noqa: F401

        import vosk  # noqa: F401

        return bool(os.environ.get(_VOSK_MODEL_DIR_ENV, "").strip())
    except Exception:
        return False
