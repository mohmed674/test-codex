from __future__ import annotations

from django.urls import path

from . import views

app_name = "backup_center"

urlpatterns = [
    path("db/", views.create_database_backup_view, name="create_database_backup"),
    path("media/", views.create_media_backup_view, name="create_media_backup"),
]
