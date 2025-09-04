# apps/templates/urls.py

from django.urls import path

from . import views

app_name = "templates"

urlpatterns = [
    path("", views.index, name="templates_index"),
]
