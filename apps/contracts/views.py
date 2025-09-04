from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContractForm
from .models import Contract


def contract_list(request):
    contracts = Contract.objects.all().order_by("-start_date")
    return render(request, "contracts/contract_list.html", {"contracts": contracts})


def create_contract(request):
    if request.method == "POST":
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("contracts:contract_list")
    else:
        form = ContractForm()
    return render(request, "contracts/contract_form.html", {"form": form})


def contract_detail(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    return render(request, "contracts/contract_detail.html", {"contract": contract})


def index(request):
    return render(request, "contracts/index.html")


def app_home(request):
    return render(request, "apps/contracts/home.html", {"app": "contracts"})
