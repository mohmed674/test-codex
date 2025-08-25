app_name = 'audit_out'
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='audit_out_index'),
]
