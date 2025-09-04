# apps/themes/urls.py

from django.urls import path

from . import views

app_name = "themes"

urlpatterns = [
    path("", views.index, name="themes_index"),
]
