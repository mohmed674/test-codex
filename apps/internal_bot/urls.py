from django.urls import path
from . import views

app_name = 'internal_bot'

urlpatterns = [
    path('', views.chat_with_bot, name='chat'),
]
