app_name = 'templates'
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='templates_index'),
]
