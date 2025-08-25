from django.urls import path
from . import views

app_name = 'departments'  # ✅ لتفعيل الأسماء النسبية (namespace)

urlpatterns = [
    # 🔍 عرض القائمة الرئيسية
    path('list/', views.department_list, name='department_list'),

    # ➕ إنشاء قسم جديد
    path('create/', views.create_department, name='department_create'),

    # ✏️ تعديل قسم
    path('edit/<int:pk>/', views.update_department, name='department_edit'),

    # 🗑️ حذف قسم
    path('delete/<int:pk>/', views.delete_department, name='department_delete'),

    # 📊 دعم API مستقبلية إن أردت:
    # path('api/list/', views.DepartmentListAPI.as_view(), name='department_list_api'),  ✅ مقترح جاهز للتنشيط لاحقًا
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
