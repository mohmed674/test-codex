from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Supplier
from .forms import SupplierForm
from core.utils import export_to_excel

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'suppliers/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('suppliers:list')
    else:
        form = SupplierForm()
    return render(request, 'suppliers/supplier_form.html', {'form': form})

@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('suppliers:list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'suppliers/supplier_form.html', {'form': form})

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        return redirect('suppliers:list')
    return render(request, 'suppliers/supplier_confirm_delete.html', {'supplier': supplier})

@login_required
def supplier_export_excel(request):
    data = [
        {
            'الاسم': s.name,
            'الهاتف': s.phone,
            'البريد': s.email,
            'العنوان': s.address,
            'المحافظة': s.governorate,
        } for s in Supplier.objects.all()
    ]
    return export_to_excel(data, filename='suppliers.xlsx')
