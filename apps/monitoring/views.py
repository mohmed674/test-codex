# ERP_CORE/monitoring/views.py

from django.db.models import Q
from django.shortcuts import redirect, render

from core.utils import export_to_excel, render_to_pdf

from .forms import DistributionOrderForm, ShipmentForm
from .models import DistributionOrder, Shipment


# 📦 إنشاء طلب توزيع
def create_order(request):
    if request.method == "POST":
        form = DistributionOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("monitoring:order_list")
    else:
        form = DistributionOrderForm()
    return render(request, "monitoring/create_order.html", {"form": form})


# 🚚 إنشاء شحنة
def create_shipment(request):
    if request.method == "POST":
        form = ShipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("monitoring:shipment_list")
    else:
        form = ShipmentForm()
    return render(request, "monitoring/create_shipment.html", {"form": form})


# 📋 قائمة الطلبات
def order_list(request):
    orders = DistributionOrder.objects.select_related("client").all()

    query = request.GET.get("q")
    status = request.GET.get("status")
    if query:
        orders = orders.filter(
            Q(client__name__icontains=query) | Q(product_name__icontains=query)
        )
    if status:
        orders = orders.filter(status=status)

    return render(
        request,
        "monitoring/order_list.html",
        {
            "orders": orders,
            "filters": {"q": query, "status": status},
        },
    )


# 📦 قائمة الشحنات
def shipment_list(request):
    shipments = Shipment.objects.select_related("order__client").all()

    tracking = request.GET.get("tracking")
    status = request.GET.get("status")
    if tracking:
        shipments = shipments.filter(tracking_number__icontains=tracking)
    if status:
        shipments = shipments.filter(status=status)

    return render(
        request,
        "monitoring/shipment_list.html",
        {
            "shipments": shipments,
            "filters": {"tracking": tracking, "status": status},
        },
    )


# 📄 تصدير الشحنات PDF
def shipment_pdf(request):
    shipments = Shipment.objects.select_related("order__client").all()
    return render_to_pdf(
        "monitoring/shipment_pdf.html", {"shipments": shipments, "request": request}
    )


# 📊 تصدير الشحنات Excel
def shipment_excel(request):
    shipments = Shipment.objects.select_related("order__client").all()
    data = [
        {
            "رقم التتبع": s.tracking_number,
            "العميل": s.order.client.name,
            "المنتج": s.order.product_name,
            "الكمية": s.order.quantity,
            "حالة الطلب": s.order.status,
            "تاريخ الشحن": s.shipped_date.strftime("%Y-%m-%d"),
            "حالة الشحنة": s.status,
        }
        for s in shipments
    ]
    return export_to_excel(data, filename="shipments.xlsx")


def index(request):
    return render(request, "monitoring/index.html")


def app_home(request):
    return render(request, "apps/monitoring/home.html", {"app": "monitoring"})
