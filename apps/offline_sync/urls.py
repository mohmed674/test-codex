from django.urls import path
from . import views

app_name = 'offline_sync'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
