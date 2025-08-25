# apps/banking/urls.py — Final routing (Sprint 3 / Banking)

from django.urls import path
from . import views

app_name = "banking"

urlpatterns = [
    # Entry / Dashboard
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Providers
    path("providers/", views.provider_list, name="provider_list"),
    path("providers/create/", views.provider_create, name="provider_create"),
    path("providers/<int:pk>/", views.provider_detail, name="provider_detail"),
    path("providers/<int:pk>/edit/", views.provider_update, name="provider_update"),
    path("providers/<int:pk>/delete/", views.provider_delete, name="provider_delete"),

    # Accounts
    path("accounts/", views.account_list, name="account_list"),
    path("accounts/create/", views.account_create, name="account_create"),
    path("accounts/<int:pk>/", views.account_detail, name="account_detail"),
    path("accounts/<int:pk>/edit/", views.account_update, name="account_update"),
    path("accounts/<int:pk>/delete/", views.account_delete, name="account_delete"),
    path("accounts/<int:pk>/statement/", views.account_statement, name="account_statement"),

    # Payments
    path("payments/", views.payment_list, name="payment_list"),
    path("payments/create/", views.payment_create, name="payment_create"),
    path("payments/<int:pk>/", views.payment_detail, name="payment_detail"),
    path("payments/<int:pk>/capture/", views.payment_capture, name="payment_capture"),
    path("payments/<int:pk>/refund/", views.payment_refund, name="payment_refund"),
    path("payments/export/csv/", views.payment_export_csv, name="payment_export_csv"),
    path("payments/export/excel/", views.payment_export_excel, name="payment_export_excel"),
    path("payments/export/pdf/", views.payment_export_pdf, name="payment_export_pdf"),

    # Transfers
    path("transfers/", views.transfer_list, name="transfer_list"),
    path("transfers/create/", views.transfer_create, name="transfer_create"),
    path("transfers/<int:pk>/", views.transfer_detail, name="transfer_detail"),
    path("transfers/<int:pk>/cancel/", views.transfer_cancel, name="transfer_cancel"),

    # Transactions (bank statements)
    path("transactions/", views.transaction_list, name="transaction_list"),
    path("transactions/import/", views.transaction_import, name="transaction_import"),

    # Reconciliation
    path("recon/", views.recon_list, name="recon_list"),
    path("recon/create/", views.recon_create, name="recon_create"),
    path("recon/<int:pk>/", views.recon_detail, name="recon_detail"),
    path("recon/<int:pk>/match/", views.recon_match, name="recon_match"),
    path("recon/<int:pk>/close/", views.recon_close, name="recon_close"),

    # Webhooks
    path("webhook/<slug:provider_code>/", views.webhook_receive, name="webhook_receive"),
]
