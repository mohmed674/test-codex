from django.urls import path
from . import views

app_name = "evaluation"

urlpatterns = [
    path('', views.evaluation_list, name="list"),
    path('add/', views.evaluation_create, name="add"),
]
