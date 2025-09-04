from __future__ import annotations

import logging
from typing import cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from apps.banking.models import BankAccount, BankProvider, Payment, Transfer
from apps.banking.services.account_service import AccountService
from apps.banking.services.provider_service import ProviderService

logger = logging.getLogger(__name__)


@login_required
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "banking/index.html")


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    context = {
        "providers": BankProvider.objects.count(),
        "accounts": BankAccount.objects.count(),
        "payments": Payment.objects.count(),
        "transfers": Transfer.objects.count(),
    }
    return render(request, "banking/dashboard.html", context)


@login_required
def provider_list(request: HttpRequest) -> HttpResponse:
    providers = BankProvider.objects.all()
    return render(request, "banking/provider_list.html", {"providers": providers})


@login_required
def provider_detail(request: HttpRequest, pk: int) -> HttpResponse:
    provider = get_object_or_404(BankProvider, pk=pk)
    return render(request, "banking/provider_detail.html", {"provider": provider})


@login_required
def provider_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        try:
            data = cast(dict[str, str], request.POST.dict())
            ProviderService.create(data)
            messages.success(request, _("Provider created successfully."))
            return redirect("banking:provider_list")
        except Exception as e:  # noqa: BLE001
            logger.exception("Error creating provider: %s", e)
            messages.error(request, _("Error creating provider."))
    return render(request, "banking/provider_form.html")


@login_required
def provider_update(request: HttpRequest, pk: int) -> HttpResponse:
    provider = get_object_or_404(BankProvider, pk=pk)
    if request.method == "POST":
        try:
            data = cast(dict[str, str], request.POST.dict())
            ProviderService.update(pk, data)
            messages.success(request, _("Provider updated."))
            return redirect("banking:provider_detail", pk=pk)
        except Exception as e:  # noqa: BLE001
            logger.exception("Error updating provider: %s", e)
            messages.error(request, _("Error updating provider."))
    return render(request, "banking/provider_form.html", {"provider": provider})


@login_required
def provider_delete(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        ProviderService.delete(pk)
        messages.success(request, _("Provider deleted."))
    except Exception as e:  # noqa: BLE001
        logger.exception("Error deleting provider: %s", e)
        messages.error(request, _("Error deleting provider."))
    return redirect("banking:provider_list")


@login_required
def account_list(request: HttpRequest) -> HttpResponse:
    accounts = BankAccount.objects.select_related("provider").all()
    return render(request, "banking/account_list.html", {"accounts": accounts})


@login_required
def account_detail(request: HttpRequest, pk: int) -> HttpResponse:
    account = get_object_or_404(BankAccount, pk=pk)
    return render(request, "banking/account_detail.html", {"account": account})


@login_required
def account_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        try:
            data = cast(dict[str, str], request.POST.dict())
            AccountService.create(data)
            messages.success(request, _("Account created successfully."))
            return redirect("banking:account_list")
        except Exception as e:  # noqa: BLE001
            logger.exception("Error creating account: %s", e)
            messages.error(request, _("Error creating account."))
    providers = BankProvider.objects.all()
    return render(request, "banking/account_form.html", {"providers": providers})


@login_required
def account_update(request: HttpRequest, pk: int) -> HttpResponse:
    account = get_object_or_404(BankAccount, pk=pk)
    if request.method == "POST":
        try:
            data = cast(dict[str, str], request.POST.dict())
            AccountService.update(pk, data)
            messages.success(request, _("Account updated."))
            return redirect("banking:account_detail", pk=pk)
        except Exception as e:  # noqa: BLE001
            logger.exception("Error updating account: %s", e)
            messages.error(request, _("Error updating account."))
    return render(request, "banking/account_form.html", {"account": account})


@login_required
def account_delete(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        AccountService.delete(pk)
        messages.success(request, _("Account deleted."))
    except Exception as e:  # noqa: BLE001
        logger.exception("Error deleting account: %s", e)
        messages.error(request, _("Error deleting account."))
    return redirect("banking:account_list")


@login_required
def account_statement(request: HttpRequest, pk: int) -> HttpResponse:
    account = get_object_or_404(BankAccount, pk=pk)
    txns = account.transactions.order_by("-booked_at")  # type: ignore[attr-defined]
    paginator = Paginator(txns, 25)
    page = request.GET.get("page")
    txns_page = paginator.get_page(page)
    return render(
        request,
        "banking/account_statement.html",
        {"account": account, "transactions": txns_page},
    )
