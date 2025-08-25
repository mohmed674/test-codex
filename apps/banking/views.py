# apps/banking/views.py — Final & Extensible (Sprint 3 / Banking)

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from .models import (
    BankProvider,
    BankAccount,
    Payment,
    Transfer,
    BankTransaction,
    ReconciliationBatch,
    WebhookEvent,
)
from django.core.paginator import Paginator
import csv
import io


# ─────────── General & Dashboard ───────────

@login_required
def index(request):
    return render(request, "banking/index.html")


@login_required
def dashboard(request):
    context = {
        "providers": BankProvider.objects.count(),
        "accounts": BankAccount.objects.count(),
        "payments": Payment.objects.count(),
        "transfers": Transfer.objects.count(),
    }
    return render(request, "banking/dashboard.html", context)


# ─────────── Providers ───────────

@login_required
def provider_list(request):
    providers = BankProvider.objects.all()
    return render(request, "banking/provider_list.html", {"providers": providers})


@login_required
def provider_detail(request, pk):
    provider = get_object_or_404(BankProvider, pk=pk)
    return render(request, "banking/provider_detail.html", {"provider": provider})


@login_required
def provider_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")
        BankProvider.objects.create(name=name, code=code)
        messages.success(request, _("Provider created successfully."))
        return redirect("banking:provider_list")
    return render(request, "banking/provider_form.html")


@login_required
def provider_update(request, pk):
    provider = get_object_or_404(BankProvider, pk=pk)
    if request.method == "POST":
        provider.name = request.POST.get("name")
        provider.code = request.POST.get("code")
        provider.save()
        messages.success(request, _("Provider updated."))
        return redirect("banking:provider_detail", pk=pk)
    return render(request, "banking/provider_form.html", {"provider": provider})


@login_required
def provider_delete(request, pk):
    provider = get_object_or_404(BankProvider, pk=pk)
    provider.delete()
    messages.success(request, _("Provider deleted."))
    return redirect("banking:provider_list")


# ─────────── Accounts ───────────

@login_required
def account_list(request):
    accounts = BankAccount.objects.select_related("provider").all()
    return render(request, "banking/account_list.html", {"accounts": accounts})


@login_required
def account_detail(request, pk):
    account = get_object_or_404(BankAccount, pk=pk)
    return render(request, "banking/account_detail.html", {"account": account})


@login_required
def account_create(request):
    if request.method == "POST":
        BankAccount.objects.create(
            provider_id=request.POST.get("provider"),
            name=request.POST.get("name"),
            account_number=request.POST.get("account_number"),
            currency=request.POST.get("currency"),
        )
        messages.success(request, _("Account created successfully."))
        return redirect("banking:account_list")
    providers = BankProvider.objects.all()
    return render(request, "banking/account_form.html", {"providers": providers})


@login_required
def account_update(request, pk):
    account = get_object_or_404(BankAccount, pk=pk)
    if request.method == "POST":
        account.name = request.POST.get("name")
        account.account_number = request.POST.get("account_number")
        account.currency = request.POST.get("currency")
        account.save()
        messages.success(request, _("Account updated."))
        return redirect("banking:account_detail", pk=pk)
    return render(request, "banking/account_form.html", {"account": account})


@login_required
def account_delete(request, pk):
    account = get_object_or_404(BankAccount, pk=pk)
    account.delete()
    messages.success(request, _("Account deleted."))
    return redirect("banking:account_list")


@login_required
def account_statement(request, pk):
    account = get_object_or_404(BankAccount, pk=pk)
    txns = account.transactions.order_by("-booked_at")
    paginator = Paginator(txns, 25)
    page = request.GET.get("page")
    txns_page = paginator.get_page(page)
    return render(request, "banking/account_statement.html", {"account": account, "transactions": txns_page})


# ─────────── Payments ───────────

@login_required
def payment_list(request):
    payments = Payment.objects.select_related("provider", "account").all()
    return render(request, "banking/payment_list.html", {"payments": payments})


@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, "banking/payment_detail.html", {"payment": payment})


@login_required
def payment_create(request):
    if request.method == "POST":
        Payment.objects.create(
            provider_id=request.POST.get("provider"),
            account_id=request.POST.get("account"),
            direction=request.POST.get("direction"),
            method=request.POST.get("method"),
            amount=request.POST.get("amount"),
            currency=request.POST.get("currency"),
            reference=request.POST.get("reference"),
        )
        messages.success(request, _("Payment created."))
        return redirect("banking:payment_list")
    return render(request, "banking/payment_form.html")


@login_required
def payment_capture(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    payment.status = "succeeded"
    payment.save()
    messages.success(request, _("Payment captured."))
    return redirect("banking:payment_detail", pk=pk)


@login_required
def payment_refund(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    payment.status = "refunded"
    payment.save()
    messages.success(request, _("Payment refunded."))
    return redirect("banking:payment_detail", pk=pk)


@login_required
def payment_export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=payments.csv"
    writer = csv.writer(response)
    writer.writerow(["Reference", "Amount", "Currency", "Status"])
    for p in Payment.objects.all():
        writer.writerow([p.reference, p.amount, p.currency, p.status])
    return response


@login_required
def payment_export_excel(request):
    return HttpResponse("Excel export not yet implemented.")


@login_required
def payment_export_pdf(request):
    return HttpResponse("PDF export not yet implemented.")


# ─────────── Transfers ───────────

@login_required
def transfer_list(request):
    transfers = Transfer.objects.all()
    return render(request, "banking/transfer_list.html", {"transfers": transfers})


@login_required
def transfer_detail(request, pk):
    transfer = get_object_or_404(Transfer, pk=pk)
    return render(request, "banking/transfer_detail.html", {"transfer": transfer})


@login_required
def transfer_create(request):
    if request.method == "POST":
        Transfer.objects.create(
            provider_id=request.POST.get("provider"),
            source_account_id=request.POST.get("source_account"),
            destination_account_id=request.POST.get("destination_account"),
            amount=request.POST.get("amount"),
            currency=request.POST.get("currency"),
            reference=request.POST.get("reference"),
        )
        messages.success(request, _("Transfer created."))
        return redirect("banking:transfer_list")
    return render(request, "banking/transfer_form.html")


@login_required
def transfer_cancel(request, pk):
    transfer = get_object_or_404(Transfer, pk=pk)
    transfer.status = "cancelled"
    transfer.save()
    messages.success(request, _("Transfer cancelled."))
    return redirect("banking:transfer_detail", pk=pk)


# ─────────── Transactions ───────────

@login_required
def transaction_list(request):
    txns = BankTransaction.objects.select_related("account").all()
    return render(request, "banking/transaction_list.html", {"transactions": txns})


@login_required
def transaction_import(request):
    if request.method == "POST" and request.FILES.get("file"):
        # Simple CSV import
        file = io.TextIOWrapper(request.FILES["file"].file, encoding="utf-8")
        reader = csv.DictReader(file)
        for row in reader:
            BankTransaction.objects.create(
                account_id=request.POST.get("account"),
                type=row.get("type"),
                amount=row.get("amount"),
                currency=row.get("currency", "EGP"),
                description=row.get("description"),
            )
        messages.success(request, _("Transactions imported."))
        return redirect("banking:transaction_list")
    return render(request, "banking/transaction_import.html")


# ─────────── Reconciliation ───────────

@login_required
def recon_list(request):
    batches = ReconciliationBatch.objects.all()
    return render(request, "banking/recon_list.html", {"batches": batches})


@login_required
def recon_detail(request, pk):
    batch = get_object_or_404(ReconciliationBatch, pk=pk)
    return render(request, "banking/recon_detail.html", {"batch": batch})


@login_required
def recon_create(request):
    if request.method == "POST":
        ReconciliationBatch.objects.create(
            provider_id=request.POST.get("provider"),
            account_id=request.POST.get("account"),
            period_start=request.POST.get("period_start"),
            period_end=request.POST.get("period_end"),
        )
        messages.success(request, _("Reconciliation batch created."))
        return redirect("banking:recon_list")
    return render(request, "banking/recon_form.html")


@login_required
def recon_match(request, pk):
    batch = get_object_or_404(ReconciliationBatch, pk=pk)
    batch.status = "matched"
    batch.save()
    messages.success(request, _("Reconciliation batch matched."))
    return redirect("banking:recon_detail", pk=pk)


@login_required
def recon_close(request, pk):
    batch = get_object_or_404(ReconciliationBatch, pk=pk)
    batch.status = "closed"
    batch.save()
    messages.success(request, _("Reconciliation batch closed."))
    return redirect("banking:recon_detail", pk=pk)


# ─────────── Webhook Receiver ───────────

@csrf_exempt
def webhook_receive(request, provider_code):
    provider = get_object_or_404(BankProvider, code=provider_code)
    WebhookEvent.objects.create(provider=provider, event_type="generic", payload=request.body.decode())
    return JsonResponse({"status": "ok"})
