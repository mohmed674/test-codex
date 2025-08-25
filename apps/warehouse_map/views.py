from django.shortcuts import render, redirect
from .models import Zone, Location
from .forms import ZoneForm, LocationForm
from django.contrib.auth.decorators import login_required

@login_required
def map_overview(request):
    zones = Zone.objects.all()
    return render(request, 'warehouse_map/map_overview.html', {'zones': zones})

@login_required
def add_zone(request):
    form = ZoneForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('warehouse_map:map_overview')
    return render(request, 'warehouse_map/zone_form.html', {'form': form})

@login_required
def add_location(request):
    form = LocationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('warehouse_map:map_overview')
    return render(request, 'warehouse_map/location_form.html', {'form': form})


from django.shortcuts import render

def index(request):
    return render(request, 'warehouse_map/index.html')


def app_home(request):
    return render(request, 'apps/warehouse_map/home.html', {'app': 'warehouse_map'})
