# ملف: ERP_CORE/inventory/urls.py

from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    # 📦 إدارة عناصر المخزون
    path('', views.inventory_list, name='inventory_list'),
    path('add/', views.add_inventory_item, name='add_inventory_item'),
    path('edit/<int:pk>/', views.edit_inventory_item, name='edit_inventory_item'),
    path('delete/<int:pk>/', views.delete_inventory_item, name='delete_inventory_item'),

    # 🔄 سجل الحركات
    path('transactions/', views.inventory_transactions, name='inventory_transactions'),
    path('transactions/add/', views.add_inventory_transaction, name='add_inventory_transaction'),

    # 📊 الجرد الفعلي الذكي (Smart Audit)
    path('audit/create/', views.create_inventory_audit, name='create_inventory_audit'),
    path('audit/<int:audit_id>/edit/', views.inventory_audit_edit, name='inventory_audit_edit'),
    path('audit/<int:audit_id>/view/', views.inventory_audit_detail, name='inventory_audit_detail'),

    # 🏬 إدارة مواقع التخزين (Warehouse)
    path('locations/', views.inventory_locations, name='inventory_locations'),
    path('locations/add/', views.add_inventory_location, name='add_inventory_location'),
    path('locations/edit/<int:pk>/', views.edit_inventory_location, name='edit_inventory_location'),
    path('locations/delete/<int:pk>/', views.delete_inventory_location, name='delete_inventory_location'),
]
