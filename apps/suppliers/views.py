from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Supplier
from .forms import SupplierForm
from core.utils import export_to_excel
from django.http import HttpResponse
from weasyprint import HTML

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'suppliers/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            # تأكد من وجود علاقة User -> Employee
            if hasattr(request.user, 'employee'):
                supplier.created_by = request.user.employee
            supplier.save()
            return redirect('suppliers:supplier_list')
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
            return redirect('suppliers:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'suppliers/supplier_form.html', {'form': form})

@login_required
def supplier_pdf(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    html = render(request, 'suppliers/supplier_pdf.html', {'supplier': supplier})
    pdf = HTML(string=html.content.decode('utf-8')).write_pdf()
    return HttpResponse(pdf, content_type='application/pdf')

@login_required
def supplier_export_excel(request):
    # تأكد من أن الحقول التالية موجودة في نموذج Supplier أو استبدلها بما يناسب
    data = [{
        'الاسم': s.name,
        'الهاتف': s.phone,
        'البريد الإلكتروني': s.email,
        'العنوان': s.address,
        'المحافظة': s.governorate,
        # 'نوع المورد': getattr(s, 'supplier_type', ''),  # إذا موجودة
        # 'الحالة': getattr(s, 'status', ''),            # إذا موجودة
    } for s in Supplier.objects.all()]
    return export_to_excel(data, filename='suppliers.xlsx')


from django.shortcuts import render

def index(request):
    return render(request, 'suppliers/index.html')


def app_home(request):
    return render(request, 'apps/suppliers/home.html', {'app': 'suppliers'})
