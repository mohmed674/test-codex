app_name = 'internal_monitoring'
# ERP_CORE/internal_monitoring/urls.py

from django.urls import path
from .views import risk_dashboard_view

urlpatterns = [
    path('dashboard/', risk_dashboard_view, name='risk_dashboard'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
