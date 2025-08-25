from django.shortcuts import render, redirect
from .models import Asset
from .forms import AssetForm
from django.contrib.auth.decorators import login_required

@login_required
def asset_list(request):
    assets = Asset.objects.all()
    return render(request, 'asset_lifecycle/asset_list.html', {'assets': assets})

@login_required
def asset_create(request):
    form = AssetForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('asset_lifecycle:asset_list')
    return render(request, 'asset_lifecycle/asset_form.html', {'form': form})


from django.shortcuts import render

def index(request):
    return render(request, 'asset_lifecycle/index.html')


def app_home(request):
    return render(request, 'apps/asset_lifecycle/home.html', {'app': 'asset_lifecycle'})
