# apps/work_regulations/urls.py — Routing normalized (Sprint 1 / Routing P1)

from django.urls import path
from . import views

app_name = 'work_regulations'

urlpatterns = [
    # Standardized index/list
    path('', views.view_work_regulation, name='index'),
    path('list/', views.view_work_regulation, name='list'),

    # Agreement route
    path('agree/<int:regulation_id>/', views.agree_to_regulation, name='agree'),

    # Legacy aliases for compatibility
    path('legacy/view/', views.view_work_regulation, name='view_work_regulation'),
    path('legacy/agree/<int:regulation_id>/', views.agree_to_regulation, name='agree_to_regulation'),
]
