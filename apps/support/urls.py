# apps/support/urls.py — Normalized (Sprint 2 / Helpdesk + Knowledge)

from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # Standardized routes
    path('', views.ticket_list, name='index'),
    path('list/', views.ticket_list, name='list'),
    path('create/', views.create_ticket, name='create'),
    path('detail/<int:pk>/', views.ticket_detail, name='detail'),
    path('update/<int:pk>/', views.add_response, name='update'),

    # Legacy aliases (for compatibility)
    path('legacy/ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('legacy/ticket/<int:pk>/response/', views.add_response, name='add_response'),
    path('legacy/ticket/create/', views.create_ticket, name='create_ticket'),
    path('legacy/tickets/', views.ticket_list, name='ticket_list'),
]
