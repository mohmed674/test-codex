# apps/banking/urls.py
# Final routing with safe fallbacks for missing views (prevents import-time errors)

from __future__ import annotations

from typing import Callable

from django.http import HttpResponse
from django.urls import path

from . import views

app_name = "banking"


def _stub(name: str) -> Callable:
    def _view(*_args, **_kwargs) -> HttpResponse:
        return HttpResponse(f"{name} is not implemented.", status=501)

    return _view


def _v(name: str) -> Callable:
    """Return view from module if present, otherwise a harmless stub."""
    return getattr(views, name, _stub(name))


urlpatterns = [
    # Entry / Dashboard
    path("", _v("index"), name="index"),
    path("dashboard/", _v("dashboard"), name="dashboard"),
    # Providers
    path("providers/", _v("provider_list"), name="provider_list"),
    path("providers/create/", _v("provider_create"), name="provider_create"),
    path("providers/<int:pk>/", _v("provider_detail"), name="provider_detail"),
    path("providers/<int:pk>/edit/", _v("provider_update"), name="provider_update"),
    path("providers/<int:pk>/delete/", _v("provider_delete"), name="provider_delete"),
    # Accounts
    path("accounts/", _v("account_list"), name="account_list"),
    path("accounts/create/", _v("account_create"), name="account_create"),
    path("accounts/<int:pk>/", _v("account_detail"), name="account_detail"),
    path("accounts/<int:pk>/edit/", _v("account_update"), name="account_update"),
    path("accounts/<int:pk>/delete/", _v("account_delete"), name="account_delete"),
    path(
        "accounts/<int:pk>/statement/",
        _v("account_statement"),
        name="account_statement",
    ),
    # Payments (some may be stubs until implemented)
    path("payments/", _v("payment_list"), name="payment_list"),
    path("payments/create/", _v("payment_create"), name="payment_create"),
    path("payments/<int:pk>/", _v("payment_detail"), name="payment_detail"),
    path("payments/<int:pk>/capture/", _v("payment_capture"), name="payment_capture"),
    path("payments/<int:pk>/refund/", _v("payment_refund"), name="payment_refund"),
    path("payments/export/csv/", _v("payment_export_csv"), name="payment_export_csv"),
    path(
        "payments/export/excel/",
        _v("payment_export_excel"),
        name="payment_export_excel",
    ),
    path("payments/export/pdf/", _v("payment_export_pdf"), name="payment_export_pdf"),
    # Transfers
    path("transfers/", _v("transfer_list"), name="transfer_list"),
    path("transfers/create/", _v("transfer_create"), name="transfer_create"),
    path("transfers/<int:pk>/", _v("transfer_detail"), name="transfer_detail"),
    path("transfers/<int:pk>/cancel/", _v("transfer_cancel"), name="transfer_cancel"),
    # Transactions (bank statements)
    path("transactions/", _v("transaction_list"), name="transaction_list"),
    path("transactions/import/", _v("transaction_import"), name="transaction_import"),
    # Reconciliation
    path("recon/", _v("recon_list"), name="recon_list"),
    path("recon/create/", _v("recon_create"), name="recon_create"),
    path("recon/<int:pk>/", _v("recon_detail"), name="recon_detail"),
    path("recon/<int:pk>/match/", _v("recon_match"), name="recon_match"),
    path("recon/<int:pk>/close/", _v("recon_close"), name="recon_close"),
    # Webhooks
    path(
        "webhook/<slug:provider_code>/", _v("webhook_receive"), name="webhook_receive"
    ),
]
