# core/urls.py
from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'core'

urlpatterns = [
    # 🚀 الواجهة الرئيسية / الإطلاق
    path('', views.launcher_view, name='launcher'),
    path('overview/', views.overview_view, name='overview'),
    path('apps/', views.launcher_view, name='apps'),

    # 📊 لوحات التحكم
    path('dashboard/', views.smart_master_dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/pdf/', views.admin_dashboard_pdf_view, name='admin_dashboard_pdf'),

    # 🧾 الوظائف (Job Titles)
    path('job-titles/', views.job_title_list, name='job_title_list'),
    path('job-titles/create/', views.job_title_create, name='job_title_create'),
    path('job-titles/<int:pk>/edit/', views.job_title_update, name='job_title_update'),
    path('job-titles/<int:pk>/delete/', views.job_title_delete, name='job_title_delete'),

    # 📏 الوحدات (Units)
    path('units/', views.unit_list, name='unit_list'),
    path('units/create/', views.unit_create, name='unit_create'),
    path('units/<int:pk>/edit/', views.unit_update, name='unit_update'),
    path('units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),

    # 📋 معايير التقييم (Evaluation Criteria)
    path('evaluation-criteria/', views.criteria_list, name='criteria_list'),
    path('evaluation-criteria/create/', views.criteria_create, name='criteria_create'),
    path('evaluation-criteria/<int:pk>/edit/', views.criteria_update, name='criteria_update'),
    path('evaluation-criteria/<int:pk>/delete/', views.criteria_delete, name='criteria_delete'),

    # 🏭 مراحل الإنتاج (Production Stages)
    path('stage-types/', views.stage_type_list, name='stage_type_list'),
    path('stage-types/create/', views.stage_type_create, name='stage_type_create'),
    path('stage-types/<int:pk>/edit/', views.stage_type_update, name='stage_type_update'),
    path('stage-types/<int:pk>/delete/', views.stage_type_delete, name='stage_type_delete'),

    # ⚠️ حدود المخاطر (Risk Thresholds)
    path('risk-thresholds/', views.risk_threshold_list, name='risk_threshold_list'),
    path('risk-thresholds/create/', views.risk_threshold_create, name='risk_threshold_create'),
    path('risk-thresholds/<int:pk>/edit/', views.risk_threshold_update, name='risk_threshold_update'),
    path('risk-thresholds/<int:pk>/delete/', views.risk_threshold_delete, name='risk_threshold_delete'),

    # 🗂️ أدوار الأقسام (Department Roles)
    path('department-roles/', views.department_role_list, name='department_role_list'),
    path('department-roles/create/', views.department_role_create, name='department_role_create'),
    path('department-roles/<int:pk>/edit/', views.department_role_update, name='department_role_update'),
    path('department-roles/<int:pk>/delete/', views.department_role_delete, name='department_role_delete'),

    # 💳 تكامل الدفع فوري (Fawry Payment Integration)
    path('payment/fawry/', views.initiate_fawry_payment, name='fawry_payment'),

    # 📴 صفحة الأوفلاين للـ PWA
    path('offline.html', TemplateView.as_view(template_name='core/offline.html'), name='offline'),

    # 🔗 Alias إضافي لـ /launcher/
    path('launcher/', views.launcher, name='launcher_alias'),

    # 🛠️ تشخيص
    path('debug/urls-health/', views.urls_health, name='urls_health'),
]
