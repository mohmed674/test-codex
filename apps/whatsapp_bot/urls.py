from django.urls import path

from . import views
from .views import \
    whatsapp_dashboard_view  # يمكنك إضافة whatsapp_settings_view لاحقًا إذا لزم الأمر

app_name = "whatsapp_bot"

urlpatterns = [
    path("dashboard/", whatsapp_dashboard_view, name="whatsapp_dashboard"),
    # path("settings/", whatsapp_settings_view, name="whatsapp_settings"),  # مفعّل لاحقًا عند الحاجة
    path("", views.app_home, name="home"),
]
