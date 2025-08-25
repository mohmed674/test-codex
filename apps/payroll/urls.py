app_name = 'payroll'
from django.urls import path
from . import views, report_views

urlpatterns = [
    path('advances/', views.advance_list, name='advance_list'),
    path('advances/add/', views.add_advance, name='add_advance'),
    path('calculate-daily-pay/<int:employee_id>/', views.calculate_daily_payment, name='calculate_daily_pay'),
    path('salaries/', views.salary_list, name='salary_list'),
    path('report/salaries/', report_views.salary_report, name='salary_report'),
    # ✅ مسار إدارة اللائحة
    path('policy-settings/', views.manage_policy_settings, name='manage_policy_settings'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
