from django.urls import path, include
from apps.suppliers import supplier_views
from apps.suppliers import reports
from apps.suppliers import api

app_name = 'suppliers'

urlpatterns = [
    path('', supplier_views.supplier_list, name='list'),
    path('add/', supplier_views.supplier_create, name='add'),
    path('<int:pk>/edit/', supplier_views.supplier_edit, name='edit'),
    # path('<int:pk>/delete/', supplier_views.supplier_delete, name='delete'),

    path('export/pdf/', reports.export_supplier_list_pdf, name='export_pdf'),
    path('export/excel/', supplier_views.supplier_export_excel, name='export_excel'),

    path('api/', include('apps.suppliers.urls.api')),


    # path('dashboard/', views.supplier_dashboard, name='dashboard'),
]
