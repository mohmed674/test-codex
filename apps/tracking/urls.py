# ERP_CORE/tracking/urls.py

from django.urls import path
from .views import (
    tracking_dashboard,
    tracking_create,
    tracking_pdf,
    tracking_excel,
    tracking_customer_view,
    tracking_movement_dashboard,
    movement_create_view,
    api_track_shipment,
    advanced_tracking_report
)

app_name = 'tracking'

urlpatterns = [
    path('dashboard/', tracking_dashboard, name='tracking_dashboard'),
    path('create/', tracking_create, name='tracking_create'),
    path('export/pdf/', tracking_pdf, name='tracking_pdf'),
    path('export/excel/', tracking_excel, name='tracking_excel'),

    # ✅ تتبع العميل
    path('customer/', tracking_customer_view, name='tracking_customer_view'),

    # ✅ حركات الشحنة
    path('movements/', tracking_movement_dashboard, name='tracking_movement_dashboard'),
    path('movements/create/', movement_create_view, name='movement_create'),

    # 🌟 API لتتبع الشحنة بكود فقط
    path('api/track/', api_track_shipment, name='api_track_shipment'),

    # 🌟 تقرير متقدم بفلترة مخصصة
    path('report/advanced/', advanced_tracking_report, name='advanced_tracking_report'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
