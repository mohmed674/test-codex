from django.shortcuts import render, get_object_or_404, redirect
from .models import Lead, Interaction, Opportunity
from .forms import LeadForm, InteractionForm, OpportunityForm

def lead_list(request):
    leads = Lead.objects.all().order_by('-created_at')
    return render(request, 'crm/lead_list.html', {'leads': leads})

def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    interactions = lead.interactions.all()
    opportunity = Opportunity.objects.filter(lead=lead).first()
    return render(request, 'crm/lead_detail.html', {
        'lead': lead,
        'interactions': interactions,
        'opportunity': opportunity
    })

def add_interaction(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        form = InteractionForm(request.POST)
        if form.is_valid():
            interaction = form.save(commit=False)
            interaction.lead = lead
            interaction.by = request.user.employee
            interaction.save()
            return redirect('crm:lead_detail', pk=pk)
    else:
        form = InteractionForm()
    return render(request, 'crm/add_interaction.html', {'form': form, 'lead': lead})

def add_opportunity(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opp = form.save(commit=False)
            opp.lead = lead
            opp.save()
            return redirect('crm:lead_detail', pk=pk)
    else:
        form = OpportunityForm()
    return render(request, 'crm/add_opportunity.html', {'form': form, 'lead': lead})


from django.shortcuts import render

def index(request):
    return render(request, 'crm/index.html')


def app_home(request):
    return render(request, 'apps/crm/home.html', {'app': 'crm'})
