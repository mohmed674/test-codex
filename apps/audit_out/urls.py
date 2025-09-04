# apps/audit_out/urls.py
from django.urls import path

from . import views

app_name = "audit_out"

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.app_home, name="app_home"),
]
