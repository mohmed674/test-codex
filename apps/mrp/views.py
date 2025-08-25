from django.shortcuts import render, redirect, get_object_or_404
from .models import MaterialPlanning, MaterialLine
from .forms import MaterialPlanningForm
from apps.production.models import BillOfMaterials
from apps.inventory.models import Inventory
from django.db.models import Sum

def planning_list(request):
    plans = MaterialPlanning.objects.all()
    return render(request, 'mrp/planning_list.html', {'plans': plans})

def planning_add(request):
    form = MaterialPlanningForm(request.POST or None)
    if form.is_valid():
        plan = form.save()
        bom = BillOfMaterials.objects.get(product=plan.product)
        for item in bom.components.all():
            required = item.quantity * plan.planned_quantity
            stock = Inventory.objects.filter(product=item.component).aggregate(total=Sum('quantity'))['total'] or 0
            shortage = required - stock
            MaterialLine.objects.create(
                planning=plan,
                material=item.component,
                required_qty=required,
                available_qty=stock,
                shortage_qty=shortage if shortage > 0 else 0,
            )
        return redirect('mrp:planning_list')
    return render(request, 'mrp/planning_form.html', {'form': form})

def planning_detail(request, pk):
    plan = get_object_or_404(MaterialPlanning, pk=pk)
    return render(request, 'mrp/planning_detail.html', {'plan': plan})


from django.shortcuts import render

def index(request):
    return render(request, 'mrp/index.html')


def app_home(request):
    return render(request, 'apps/mrp/home.html', {'app': 'mrp'})
