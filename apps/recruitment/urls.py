from django.urls import path
from . import views

app_name = 'recruitment'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
]
