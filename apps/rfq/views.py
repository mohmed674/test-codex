from django.shortcuts import render, redirect, get_object_or_404
from .models import RFQ, RFQItem, RFQResponse
from .forms import RFQForm
from apps.suppliers.models import Supplier
from apps.products.models import Product
from django.contrib.auth.decorators import login_required

@login_required
def rfq_list(request):
    rfqs = RFQ.objects.all()
    return render(request, 'rfq/rfq_list.html', {'rfqs': rfqs})

@login_required
def rfq_create(request):
    form = RFQForm(request.POST or None)
    if form.is_valid():
        rfq = form.save(commit=False)
        rfq.created_by = request.user
        rfq.save()
        # افتراضي: طلب عروض لجميع الموردين
        for supplier in Supplier.objects.all():
            rfq_response = RFQResponse.objects.create(rfq=rfq, supplier=supplier)
        return redirect('rfq:rfq_list')
    return render(request, 'rfq/rfq_form.html', {'form': form})

@login_required
def rfq_detail(request, pk):
    rfq = get_object_or_404(RFQ, pk=pk)
    responses = RFQResponse.objects.filter(rfq=rfq)
    return render(request, 'rfq/rfq_detail.html', {'rfq': rfq, 'responses': responses})


from django.shortcuts import render

def index(request):
    return render(request, 'rfq/index.html')


def app_home(request):
    return render(request, 'apps/rfq/home.html', {'app': 'rfq'})
