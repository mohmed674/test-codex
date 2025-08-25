from django.urls import path
from . import views

app_name = 'risk_management'

urlpatterns = [
    path('', views.risk_list, name='risk_list'),
    path('add/', views.risk_add, name='risk_add'),
    path('<int:pk>/', views.risk_detail, name='risk_detail'),
]
