# apps/clients/urls.py — Routing normalized (Sprint 1 / Routing P1)

from django.urls import path

from . import views

app_name = "clients"

urlpatterns = [
    # Standardized routes (namespace = 'clients', names = index/list/create/update/delete)
    path("", views.client_list, name="index"),  # alias للصفحة الرئيسية
    path("list/", views.client_list, name="list"),
    path("create/", views.client_create, name="create"),
    path("update/<int:pk>/", views.client_update, name="update"),
    path("delete/<int:pk>/", views.client_delete, name="delete"),
    # Legacy name aliases (توافق القوالب القديمة إن وُجدت)
    path("legacy/list/", views.client_list, name="client_list"),
    # Extras
    path("ai/<int:pk>/", views.client_ai_insight, name="ai_insight"),
    path("pdf/<int:pk>/", views.client_pdf_view, name="pdf"),
    path("analysis/", views.client_analysis_dashboard, name="analysis"),
]
