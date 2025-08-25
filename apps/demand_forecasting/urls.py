# apps/demand_forecasting/urls.py — Routing normalized (Sprint 1 / Routing P1)

from django.urls import path
from . import views

app_name = 'demand_forecasting'

urlpatterns = [
    # Standardized routes
    path('', views.forecast_list, name='index'),
    path('list/', views.forecast_list, name='list'),
    path('create/', views.forecast_generate, name='create'),

    # Legacy aliases (compatibility with old templates)
    path('legacy/list/', views.forecast_list, name='forecast_list'),
    path('legacy/generate/', views.forecast_generate, name='forecast_generate'),
]
