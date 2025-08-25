# apps/workflow/urls.py — Routing normalized (Sprint 1 / Routing P1)

from django.urls import path
from . import views

app_name = 'workflow'

urlpatterns = [
    # Standardized routes
    path('', views.workflow_list, name='index'),
    path('list/', views.workflow_list, name='list'),
    path('create/', views.workflow_create, name='create'),

    # Legacy alias (for backward compatibility)
    path('legacy/list/', views.workflow_list, name='workflow_list'),
    path('legacy/create/', views.workflow_create, name='workflow_create'),
]
