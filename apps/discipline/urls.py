app_name = 'discipline'
from django.urls import path
from . import views
from . import report_views

urlpatterns = [
    path('discipline/list/', views.discipline_list, name='discipline_list'),
    path('discipline/report/', report_views.discipline_report, name='discipline_report'),
    path('discipline/manager-report/', report_views.manager_discipline_report, name='manager_discipline_report'),
    path('employee/<int:employee_id>/profile/', views.employee_discipline_history, name='employee_profile'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
