app_name = 'attendance'
from django.urls import path
from . import views
from .reports import attendance_reports as report_views  # ✅ تحديث المسار الجديد

urlpatterns = [
    # 🔹 views.py
    path('list/', views.attendance_list, name='attendance_list'),
    path('print/', views.attendance_print_view, name='attendance_print'),
    path('create/', views.attendance_create, name='attendance_create'),

    # 🔹 attendance_reports.py داخل reports/
    path('report/', report_views.attendance_report, name='attendance_report'),
    path('report/pdf/', report_views.attendance_report_pdf, name='attendance_report_pdf'),
    path('report/excel/', report_views.attendance_report_excel, name='attendance_report_excel'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
