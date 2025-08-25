# apps/suppliers/urls.py — Routing normalized (Sprint 1 / Routing P1)

from django.urls import path, include
from . import supplier_views, reports, api

app_name = 'suppliers'

urlpatterns = [
    # Standardized core CRUD routes (namespace = 'suppliers')
    path('', supplier_views.supplier_list, name='index'),     # alias للقائمة الرئيسية
    path('list/', supplier_views.supplier_list, name='list'),
    path('create/', supplier_views.supplier_create, name='create'),
    path('update/<int:pk>/', supplier_views.supplier_edit, name='update'),
    path('delete/<int:pk>/', supplier_views.supplier_delete, name='delete'),

    # Export options
    path('export/pdf/', reports.export_supplier_list_pdf, name='export_pdf'),
    path('export/excel/', supplier_views.supplier_export_excel, name='export_excel'),

    # API sub-routes
    path('api/', include('apps.suppliers.urls.api')),

    # Optional dashboard (can be expanded later)
    # path('dashboard/', supplier_views.supplier_dashboard, name='dashboard'),
]
