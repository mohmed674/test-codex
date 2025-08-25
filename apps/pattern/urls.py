# ERP_CORE/pattern/urls.py

from django.urls import path
from . import views

app_name = 'pattern'

urlpatterns = [
    # لوحة التحكم
    path('dashboard/', views.pattern_dashboard, name='dashboard'),

    # التصميمات
    path('designs/', views.design_list_view, name='design_list'),
    path('designs/create/', views.design_create_view, name='design_create'),

    # القطع المرتبطة بالتصميم
    path('designs/<int:design_id>/pieces/', views.piece_list_view, name='piece_list'),
    path('designs/<int:design_id>/pieces/create/', views.piece_create_view, name='piece_create'),

    # التنفيذ
    path('executions/', views.execution_list_view, name='execution_list'),
    path('executions/create/', views.execution_create_view, name='execution_create'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
