# apps/client_portal/urls.py — Normalized (Sprint 2 / Helpdesk + Knowledge)

from django.urls import path
from . import views

app_name = 'client_portal'

urlpatterns = [
    # Standardized routes
    path('', views.dashboard, name='index'),
    path('list/', views.dashboard, name='list'),
    path('create/', views.submit_ticket, name='create'),

    # Legacy aliases (backward compatibility)
    path('legacy/dashboard/', views.dashboard, name='dashboard'),
    path('legacy/ticket/', views.submit_ticket, name='submit_ticket'),
]
