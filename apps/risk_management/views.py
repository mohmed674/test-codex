from django.shortcuts import get_object_or_404, redirect, render

from .forms import RiskForm
from .models import Risk


def risk_list(request):
    risks = Risk.objects.all()
    return render(request, "risk_management/risk_list.html", {"risks": risks})


def risk_add(request):
    form = RiskForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("risk_management:risk_list")
    return render(request, "risk_management/risk_form.html", {"form": form})


def risk_detail(request, pk):
    risk = get_object_or_404(Risk, pk=pk)
    return render(request, "risk_management/risk_detail.html", {"risk": risk})


def index(request):
    return render(request, "risk_management/index.html")


def app_home(request):
    return render(request, "apps/risk_management/home.html", {"app": "risk_management"})
