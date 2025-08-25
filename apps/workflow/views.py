from django.shortcuts import render, redirect
from .models import WorkflowRule
from .forms import WorkflowRuleForm
from django.contrib.auth.decorators import login_required

@login_required
def workflow_list(request):
    rules = WorkflowRule.objects.all()
    return render(request, 'workflow/workflow_list.html', {'rules': rules})

@login_required
def workflow_create(request):
    form = WorkflowRuleForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('workflow:workflow_list')
    return render(request, 'workflow/workflow_form.html', {'form': form})


from django.shortcuts import render

def index(request):
    return render(request, 'workflow/index.html')


def app_home(request):
    return render(request, 'apps/workflow/home.html', {'app': 'workflow'})
