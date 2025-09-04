from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "dark_mode"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="dark_mode/overview.html"),
        name="overview",
    ),
    path("", views.app_home, name="home"),
]
