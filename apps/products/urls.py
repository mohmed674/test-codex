# ERP_CORE/products/urls.py

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # 📦 قائمة المنتجات
    path('', views.product_list, name='product_list'),
    path('list/', views.product_list, name='product_list_alias'),  # مسار بديل ثابت

    # ➕ إضافة منتج
    path('create/', views.product_create, name='product_create'),
    path('add/', views.product_create, name='product_add'),        # مسار بديل ثابت

    # ✏️ تعديل / ❌ حذف
    path('<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
]
