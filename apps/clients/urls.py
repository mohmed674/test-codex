# apps/clients/urls.py  — Routing normalized (Sprint 1 / Routing P1)

app_name = 'clients'
from django.urls import path
from . import views

urlpatterns = [
    # Standardized routes (namespace = 'clients', names = index/list/create/update/delete)
    path('', views.client_list, name='index'),                 # alias للصفحة الرئيسية (قائمة العملاء)
    path('list/', views.client_list, name='list'),
    path('create/', views.client_create, name='create'),
    path('update/<int:pk>/', views.client_update, name='update'),
    path('delete/<int:pk>/', views.client_delete, name='delete'),

    # Legacy name aliases (لضمان توافق القوالب القديمة إن وُجدت)
    path('legacy/list/', views.client_list, name='client_list'),

    # Extras (تبقى كما هي لكن بأسماء واضحة)
    path('ai/<int:pk>/', views.client_ai_insight, name='ai_insight'),
    path('pdf/<int:pk>/', views.client_pdf_view, name='pdf'),
    path('analysis/', views.client_analysis_dashboard, name='analysis'),
]
