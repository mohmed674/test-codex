from django.urls import path
from django.views.generic import TemplateView

app_name = "dark_mode"

urlpatterns = [
    path("", TemplateView.as_view(template_name="dark_mode/overview.html"), name="overview"),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
