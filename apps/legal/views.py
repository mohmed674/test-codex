from django.shortcuts import render, redirect, get_object_or_404
from .models import LegalCase
from .forms import LegalCaseForm

def legal_case_list(request):
    cases = LegalCase.objects.all().order_by('-created_at')
    return render(request, 'legal/legal_case_list.html', {'cases': cases})

def create_legal_case(request):
    if request.method == 'POST':
        form = LegalCaseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('legal:legal_case_list')
    else:
        form = LegalCaseForm()
    return render(request, 'legal/legal_case_form.html', {'form': form})

def legal_case_detail(request, pk):
    case = get_object_or_404(LegalCase, pk=pk)
    return render(request, 'legal/legal_case_detail.html', {'case': case})


from django.shortcuts import render

def index(request):
    return render(request, 'legal/index.html')


def app_home(request):
    return render(request, 'apps/legal/home.html', {'app': 'legal'})
