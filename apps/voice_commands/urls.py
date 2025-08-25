app_name = 'voice_commands'
from django.urls import path
from .views import upload_voice, voice_logs

urlpatterns = [
    path('upload/', upload_voice, name='upload_voice'),
    path('logs/', voice_logs, name='voice_logs'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
