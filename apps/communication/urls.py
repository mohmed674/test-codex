from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    path('', views.thread_list, name='thread_list'),
    path('<int:thread_id>/', views.thread_chat, name='thread_chat'),
]
