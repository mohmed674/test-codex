from django.urls import path
from . import views

app_name = 'legal'

urlpatterns = [
    path('', views.legal_case_list, name='legal_case_list'),
    path('create/', views.create_legal_case, name='create_legal_case'),
    path('<int:pk>/', views.legal_case_detail, name='legal_case_detail'),
]
