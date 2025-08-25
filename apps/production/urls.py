from django.urls import path
from . import views

app_name = "production"

urlpatterns = [
    path('', views.production_dashboard_view, name='dashboard'),                          # 🧠 لوحة التحكم
    path('log/', views.add_production, name='log_production'),                            # ✅ تسجيل دخول القسم
    path('orders/', views.order_list_view, name='order_list'),                            # 📄 قائمة أوامر الإنتاج
    path('orders/add/', views.order_create_view, name='order_add'),                       # ➕ إضافة أمر إنتاج
    path('consumptions/', views.consumption_list_view, name='consumption_list'),          # 📦 قائمة الاستهلاكات
    path('consumptions/add/', views.consumption_create_view, name='consumption_add'),     # ➕ إضافة استهلاك خام
]
