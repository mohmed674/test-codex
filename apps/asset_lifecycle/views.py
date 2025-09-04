from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import AssetForm
from .models import Asset


@login_required
def asset_list(request: HttpRequest) -> HttpResponse:
    assets = Asset.objects.all()
    return render(request, "asset_lifecycle/asset_list.html", {"assets": assets})


@login_required
def asset_create(request: HttpRequest) -> HttpResponse:
    form = AssetForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("asset_lifecycle:asset_list")
    return render(request, "asset_lifecycle/asset_form.html", {"form": form})


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "asset_lifecycle/index.html")


def app_home(request: HttpRequest) -> HttpResponse:
    return render(request, "apps/asset_lifecycle/home.html", {"app": "asset_lifecycle"})
