from django.urls import path
from . import views

app_name = 'theme_manager'

urlpatterns = [
    path('', views.overview, name='overview'),        # /theme-manager/
    path('overview/', views.overview, name='home'),   # /theme-manager/overview/
]
