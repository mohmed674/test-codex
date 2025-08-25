from django.urls import path
from . import views

app_name = 'rfq'

urlpatterns = [
    path('', views.rfq_list, name='rfq_list'),
    path('create/', views.rfq_create, name='rfq_create'),
    path('<int:pk>/', views.rfq_detail, name='rfq_detail'),
]
