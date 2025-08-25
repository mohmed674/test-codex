app_name = 'whatsapp_bot'
from django.urls import path
from .views import (
    whatsapp_dashboard_view,
    # whatsapp_settings_view  # معلق أو حذف إذا لم تستخدمها
)

urlpatterns = [
    path('dashboard/', whatsapp_dashboard_view, name='whatsapp_dashboard'),
    # أضف مسارات أخرى حسب الحاجة
    # path('settings/', whatsapp_settings_view, name='whatsapp_settings'),  # إذا أضفت الفيو لاحقًا
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
