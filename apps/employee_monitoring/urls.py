from django.urls import path
from . import views

app_name = 'employee_monitoring'

urlpatterns = [
    path('input/', views.monitoring_input, name='monitoring_input'),
    path('dashboard/', views.monitoring_dashboard, name='monitoring_dashboard'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
