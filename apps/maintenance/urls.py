from django.urls import path

from . import views
from .views import (log_maintenance, maintenance_logs, maintenance_logs_excel,
                    maintenance_logs_pdf)

app_name = "maintenance"

urlpatterns = [
    path("log/", log_maintenance, name="log_maintenance"),  # 🛠️ تسجيل صيانة
    path("logs/", maintenance_logs, name="maintenance_logs"),  # 📋 عرض السجل
    path("logs/pdf/", maintenance_logs_pdf, name="maintenance_logs_pdf"),  # 🖨️ تصدير PDF
    path(
        "logs/excel/", maintenance_logs_excel, name="maintenance_logs_excel"
    ),  # 📊 تصدير Excel
    path("", views.app_home, name="home"),
]
