from django.shortcuts import get_object_or_404, redirect, render

from .forms import LegalCaseForm
from .models import LegalCase


def legal_case_list(request):
    cases = LegalCase.objects.all().order_by("-created_at")
    return render(request, "legal/legal_case_list.html", {"cases": cases})


def create_legal_case(request):
    if request.method == "POST":
        form = LegalCaseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("legal:legal_case_list")
    else:
        form = LegalCaseForm()
    return render(request, "legal/legal_case_form.html", {"form": form})


def legal_case_detail(request, pk):
    case = get_object_or_404(LegalCase, pk=pk)
    return render(request, "legal/legal_case_detail.html", {"case": case})


def index(request):
    return render(request, "legal/index.html")


def app_home(request):
    return render(request, "apps/legal/home.html", {"app": "legal"})
