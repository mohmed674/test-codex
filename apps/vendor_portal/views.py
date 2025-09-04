from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.accounting.models import SupplierInvoice
from apps.purchases.models import PurchaseOrder


@login_required
def portal_home(request):
    supplier = request.user.supplier  # كل مستخدم مربوط بمورد
    orders = PurchaseOrder.objects.filter(supplier=supplier)
    invoices = SupplierInvoice.objects.filter(supplier=supplier)
    return render(
        request,
        "vendor_portal/dashboard.html",
        {
            "orders": orders,
            "invoices": invoices,
        },
    )


def index(request):
    return render(request, "vendor_portal/index.html")


def app_home(request):
    return render(request, "apps/vendor_portal/home.html", {"app": "vendor_portal"})
