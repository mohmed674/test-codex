from django.shortcuts import render, get_object_or_404, redirect
from .models import SupportTicket
from .forms import SupportTicketForm, SupportResponseForm

def ticket_list(request):
    tickets = SupportTicket.objects.all().order_by('-created_at')
    return render(request, 'support/ticket_list.html', {'tickets': tickets})

def ticket_detail(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk)
    responses = ticket.responses.all()
    return render(request, 'support/ticket_detail.html', {'ticket': ticket, 'responses': responses})

def create_ticket(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('support:ticket_list')
    else:
        form = SupportTicketForm()
    return render(request, 'support/ticket_form.html', {'form': form})

def add_response(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk)
    if request.method == 'POST':
        form = SupportResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.responder = request.user.employee
            response.save()
            return redirect('support:ticket_detail', pk=pk)
    else:
        form = SupportResponseForm()
    return render(request, 'support/response_form.html', {'form': form, 'ticket': ticket})


from django.shortcuts import render

def index(request):
    return render(request, 'support/index.html')


def app_home(request):
    return render(request, 'apps/support/home.html', {'app': 'support'})
