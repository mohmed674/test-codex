from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.purchases.models import PurchaseOrder
from apps.accounting.models import SupplierInvoice
from apps.suppliers.models import Supplier

@login_required
def portal_home(request):
    supplier = request.user.supplier  # كل مستخدم مربوط بمورد
    orders = PurchaseOrder.objects.filter(supplier=supplier)
    invoices = SupplierInvoice.objects.filter(supplier=supplier)
    return render(request, 'vendor_portal/dashboard.html', {
        'orders': orders,
        'invoices': invoices,
    })


from django.shortcuts import render

def index(request):
    return render(request, 'vendor_portal/index.html')


def app_home(request):
    return render(request, 'apps/vendor_portal/home.html', {'app': 'vendor_portal'})
