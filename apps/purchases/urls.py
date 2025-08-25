# ERP_CORE/purchases/urls.py

from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('request/new/', views.purchase_request_create, name='purchase_request_create'),
    path('', views.purchase_list, name='purchase_list'),
    path('order/<int:request_id>/', views.purchase_order_create, name='purchase_order_create'),
    path('invoice/<int:order_id>/', views.purchase_invoice_create, name='purchase_invoice_create'),
]
