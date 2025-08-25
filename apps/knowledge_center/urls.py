# apps/knowledge_center/urls.py — Normalized (Sprint 2 / Helpdesk + Knowledge)

from django.urls import path
from . import views

app_name = 'knowledge_center'

urlpatterns = [
    # Standardized routes
    path('', views.article_list, name='index'),
    path('list/', views.article_list, name='list'),
    path('create/', views.article_create, name='create'),

    # Legacy aliases (for backward compatibility)
    path('legacy/articles/', views.article_list, name='article_list'),
    path('legacy/articles/create/', views.article_create, name='article_create'),
]
