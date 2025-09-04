from django.apps import apps as _dj_apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.contracts.models import Contract
from apps.sales.models import SaleInvoice
from .forms import SupportTicketForm
from .models import ClientAccess


def _get_support_ticket_model():
    """
    اجلب نموذج SupportTicket بشكل كسول لتفادي LookupError أثناء إقلاع السيرفر
    (عند استيراد urls قبل اكتمال جاهزية سجل التطبيقات).
    """
    try:
        # require_ready=False يسمح بالوصول قبل اكتمال populate()
        return _dj_apps.get_model("support", "SupportTicket", require_ready=False)  # type: ignore[call-arg]
    except Exception:
        return None


@login_required
def dashboard(request):
    try:
        access = ClientAccess.objects.get(user=request.user)
        client = access.client
    except ClientAccess.DoesNotExist:
        client = getattr(request.user, "client", None)

    SupportTicket = _get_support_ticket_model()

    if client:
        invoices = SaleInvoice.objects.filter(client=client)
        if SupportTicket is not None:
            tickets = SupportTicket.objects.filter(client=client)  # type: ignore[attr-defined]
        else:
            tickets = []
        contracts = Contract.objects.filter(client=client)
    else:
        invoices = SaleInvoice.objects.none()
        tickets = SupportTicket.objects.none() if SupportTicket is not None else []  # type: ignore[attr-defined]
        contracts = Contract.objects.none()

    context = {
        "invoices": invoices,
        "tickets": tickets,
        "contracts": contracts,
    }
    return render(request, "client_portal/dashboard.html", context)


@login_required
def submit_ticket(request):
    try:
        access = ClientAccess.objects.get(user=request.user)
        client = access.client
    except ClientAccess.DoesNotExist:
        client = getattr(request.user, "client", None)

    form = SupportTicketForm(request.POST or None)
    if form.is_valid() and client is not None:
        ticket = form.save(commit=False)
        # اربط بالعميل إن كان نموذج التذاكر متاحًا
        SupportTicket = _get_support_ticket_model()
        if SupportTicket is not None:
            ticket.client = client  # type: ignore[attr-defined]
        ticket.save()
        return redirect("client_portal:dashboard")

    return render(request, "client_portal/submit_ticket.html", {"form": form})


def index(request):
    return render(request, "client_portal/index.html")


def app_home(request):
    return render(request, "apps/client_portal/home.html", {"app": "client_portal"})
