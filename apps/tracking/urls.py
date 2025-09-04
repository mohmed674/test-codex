from django.urls import path

from . import views
from .views import (advanced_tracking_report, api_track_shipment,
                    movement_create_view, tracking_create,
                    tracking_customer_view, tracking_dashboard, tracking_excel,
                    tracking_movement_dashboard, tracking_pdf)

app_name = "tracking"

urlpatterns = [
    path("dashboard/", tracking_dashboard, name="tracking_dashboard"),
    path("create/", tracking_create, name="tracking_create"),
    path("export/pdf/", tracking_pdf, name="tracking_pdf"),
    path("export/excel/", tracking_excel, name="tracking_excel"),
    # ✅ تتبع العميل
    path("customer/", tracking_customer_view, name="tracking_customer_view"),
    # ✅ حركات الشحنة
    path("movements/", tracking_movement_dashboard, name="tracking_movement_dashboard"),
    path("movements/create/", movement_create_view, name="movement_create"),
    # 🌟 API لتتبع الشحنة بكود فقط
    path("api/track/", api_track_shipment, name="api_track_shipment"),
    # 🌟 تقرير متقدم بفلترة مخصصة
    path("report/advanced/", advanced_tracking_report, name="advanced_tracking_report"),
    path("", views.app_home, name="home"),
]
