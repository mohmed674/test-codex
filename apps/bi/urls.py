from django.urls import path
from . import views

app_name = 'bi'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('sales/', views.sales_analytics, name='sales_analytics'),
    path('clients/', views.client_analytics, name='client_analytics'),
    path('finance/', views.financial_analytics, name='financial_analytics'),
    path('export/pdf/', views.export_bi_pdf, name='export_bi_pdf'),
    path('export/excel/', views.export_bi_excel, name='export_bi_excel'),
]
