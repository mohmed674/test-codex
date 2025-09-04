from django.urls import path

from . import views
from .views import (create_order, create_shipment, order_list, shipment_excel,
                    shipment_list, shipment_pdf)

app_name = "monitoring"

urlpatterns = [
    path("orders/create/", create_order, name="create_order"),  # 📝 إنشاء طلب توزيع
    path("orders/", order_list, name="order_list"),  # 📋 عرض الطلبات
    path("shipments/create/", create_shipment, name="create_shipment"),  # 🚚 إنشاء شحنة
    path("shipments/", shipment_list, name="shipment_list"),  # 📦 عرض الشحنات
    path("shipments/pdf/", shipment_pdf, name="shipment_pdf"),  # 📄 تصدير PDF
    path("shipments/excel/", shipment_excel, name="shipment_excel"),  # 📊 تصدير Excel
    path("", views.app_home, name="home"),
]
