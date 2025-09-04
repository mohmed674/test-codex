from __future__ import annotations

import io

from django.urls import reverse


def test_stt_status_ok(client):
    url = reverse("voice_commands:stt_status")
    resp = client.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True


def test_upload_voice_missing_file(client):
    url = reverse("voice_commands:upload_voice")
    resp = client.post(url, {})
    assert resp.status_code == 400
    assert resp.json()["ok"] is False


def test_upload_voice_small_wav(client, settings):
    # WAV رأسية صغيرة جداً (مش صوت حقيقي) — فقط للتأكد من المسار
    url = reverse("voice_commands:upload_voice")
    fake_wav = io.BytesIO(b"RIFF\x24\x80\x00\x00WAVEfmt ")
    fake_wav.name = "test.wav"
    resp = client.post(url, {"file": fake_wav, "language": "ar-EG"})
    # قد يفشل التفريغ لكن يجب أن يرجع 422/503 وليس 500
    assert resp.status_code in (200, 422, 503)
