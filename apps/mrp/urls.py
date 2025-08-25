from django.urls import path
from . import views

app_name = 'mrp'

urlpatterns = [
    path('', views.planning_list, name='planning_list'),
    path('add/', views.planning_add, name='planning_add'),
    path('<int:pk>/', views.planning_detail, name='planning_detail'),
]
