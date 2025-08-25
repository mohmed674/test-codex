# apps/mobile/urls.py — Normalized (Sprint 3 / Mobile PWA + REST)

from django.urls import path
from . import views

app_name = "mobile"

urlpatterns = [
    # Standardized entry
    path("", views.mobile_dashboard, name="index"),
    path("list/", views.mobile_dashboard, name="list"),

    # REST / API endpoints (PWA-ready)
    path("api/session/", views.api_session, name="api_session"),
    path("api/menu/", views.api_menu, name="api_menu"),
    path("api/offline/sync/", views.api_offline_sync, name="api_offline_sync"),
    path("api/notifications/", views.api_notifications, name="api_notifications"),

    # Legacy alias
    path("legacy/dashboard/", views.mobile_dashboard, name="dashboard"),
]
