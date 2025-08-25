app_name = 'themes'
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='themes_index'),
]
