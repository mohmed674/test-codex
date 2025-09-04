from django.urls import path

from . import views
from .views import risk_dashboard_view

app_name = "internal_monitoring"

urlpatterns = [
    path("dashboard/", risk_dashboard_view, name="risk_dashboard"),
    path("", views.app_home, name="home"),
]
