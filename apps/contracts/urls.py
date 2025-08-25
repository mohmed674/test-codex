from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.contract_list, name='contract_list'),
    path('create/', views.create_contract, name='create_contract'),
    path('<int:pk>/', views.contract_detail, name='contract_detail'),
]
