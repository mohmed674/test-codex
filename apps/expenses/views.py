from django.shortcuts import render, redirect
from .models import Expense
from .forms import ExpenseForm
from django.contrib.auth.decorators import login_required

@login_required
def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'expenses/expense_list.html', {'expenses': expenses})

@login_required
def expense_create(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('expenses:expense_list')
    return render(request, 'expenses/expense_form.html', {'form': form})


from django.shortcuts import render

def index(request):
    return render(request, 'expenses/index.html')


def app_home(request):
    return render(request, 'apps/expenses/home.html', {'app': 'expenses'})
