from __future__ import annotations

from django.urls import path

from . import views

app_name = "voice_commands"

urlpatterns = [
    path("upload/", views.upload_voice, name="upload_voice"),
    path("status/", views.stt_status, name="stt_status"),
    path("logs/", views.voice_logs, name="voice_logs"),
]
