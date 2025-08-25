# apps/warehouse_map/urls.py — Routing normalized (Sprint 1 / Routing P1)

from django.urls import path
from . import views

app_name = 'warehouse_map'

urlpatterns = [
    # Standardized routes (namespace = 'warehouse_map')
    path('', views.map_overview, name='index'),
    path('list/', views.map_overview, name='list'),
    path('create/zone/', views.add_zone, name='create_zone'),
    path('create/location/', views.add_location, name='create_location'),

    # Aliases for backward compatibility (legacy naming if used in templates)
    path('overview/', views.map_overview, name='map_overview'),
    path('zone/add/', views.add_zone, name='add_zone'),
    path('location/add/', views.add_location, name='add_location'),
]
