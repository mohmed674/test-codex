from django.urls import path
from . import views

app_name = 'backup_center'

urlpatterns = [
    path('', views.backup_dashboard, name='dashboard'),
]
