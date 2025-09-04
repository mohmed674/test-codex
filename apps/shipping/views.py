from django.shortcuts import get_object_or_404, redirect, render

from .forms import ShipmentForm
from .models import Shipment


def shipment_list(request):
    shipments = Shipment.objects.all().order_by("-shipping_date")
    return render(request, "shipping/shipment_list.html", {"shipments": shipments})


def create_shipment(request):
    if request.method == "POST":
        form = ShipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("shipping:shipment_list")
    else:
        form = ShipmentForm()
    return render(request, "shipping/shipment_form.html", {"form": form})


def update_shipment(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    if request.method == "POST":
        form = ShipmentForm(request.POST, instance=shipment)
        if form.is_valid():
            form.save()
            return redirect("shipping:shipment_list")
    else:
        form = ShipmentForm(instance=shipment)
    return render(request, "shipping/shipment_form.html", {"form": form})


def track_shipment(request, tracking_number):
    shipment = get_object_or_404(Shipment, tracking_number=tracking_number)
    return render(request, "shipping/shipment_track.html", {"shipment": shipment})


def index(request):
    return render(request, "shipping/index.html")


def app_home(request):
    return render(request, "apps/shipping/home.html", {"app": "shipping"})
