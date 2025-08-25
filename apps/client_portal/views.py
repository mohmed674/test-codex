from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import ClientAccess
from apps.support.models import SupportTicket
from apps.sales.models import SaleInvoice  # حذف Invoice لأنه غير موجود في sales.models
from apps.contracts.models import Contract
from .forms import SupportTicketForm

@login_required
def dashboard(request):
    try:
        access = ClientAccess.objects.get(user=request.user)
        client = access.client
    except ClientAccess.DoesNotExist:
        client = getattr(request.user, 'client', None)

    if client:
        # هنا عدل شرط الفلترة، لأن SaleInvoice يستخدم client وليس customer
        invoices = SaleInvoice.objects.filter(client=client)
        tickets = SupportTicket.objects.filter(client=client)
        contracts = Contract.objects.filter(client=client)
    else:
        invoices = SaleInvoice.objects.none()
        tickets = SupportTicket.objects.none()
        contracts = Contract.objects.none()

    context = {
        'invoices': invoices,
        'tickets': tickets,
        'contracts': contracts,
    }
    return render(request, 'client_portal/dashboard.html', context)

@login_required
def submit_ticket(request):
    try:
        access = ClientAccess.objects.get(user=request.user)
        client = access.client
    except ClientAccess.DoesNotExist:
        client = getattr(request.user, 'client', None)

    form = SupportTicketForm(request.POST or None)
    if form.is_valid() and client is not None:
        ticket = form.save(commit=False)
        ticket.client = client
        ticket.save()
        return redirect('client_portal:dashboard')

    return render(request, 'client_portal/submit_ticket.html', {'form': form})


from django.shortcuts import render

def index(request):
    return render(request, 'client_portal/index.html')


def app_home(request):
    return render(request, 'apps/client_portal/home.html', {'app': 'client_portal'})
