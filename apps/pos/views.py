from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import POSSession, POSOrder, POSOrderItem
from .forms import POSOrderForm, POSOrderItemForm
from django.forms import modelformset_factory

def open_session(request):
    if request.method == 'POST':
        session = POSSession.objects.create(
            name=f"Session-{timezone.now().strftime('%Y%m%d%H%M')}",
            cashier=request.user.employee
        )
        return redirect('pos:new_order', session_id=session.id)
    return render(request, 'pos/open_session.html')

def close_session(request, session_id):
    session = get_object_or_404(POSSession, id=session_id)
    session.end_time = timezone.now()
    session.is_closed = True
    session.save()
    return redirect('pos:open_session')

def new_order(request, session_id):
    session = get_object_or_404(POSSession, id=session_id)
    OrderItemFormSet = modelformset_factory(POSOrderItem, form=POSOrderItemForm, extra=3)

    if request.method == 'POST':
        order_form = POSOrderForm(request.POST)
        formset = OrderItemFormSet(request.POST, queryset=POSOrderItem.objects.none())
        if order_form.is_valid() and formset.is_valid():
            order = order_form.save(commit=False)
            order.session = session
            order.total = 0
            order.save()
            for form in formset:
                item = form.save(commit=False)
                item.order = order
                item.save()
                order.total += item.subtotal()
            order.save()
            return redirect('pos:order_detail', order_id=order.id)
    else:
        order_form = POSOrderForm()
        formset = OrderItemFormSet(queryset=POSOrderItem.objects.none())

    return render(request, 'pos/new_order.html', {
        'order_form': order_form,
        'formset': formset,
        'session': session
    })

def order_detail(request, order_id):
    order = get_object_or_404(POSOrder, id=order_id)
    return render(request, 'pos/order_detail.html', {'order': order})


from django.shortcuts import render

def index(request):
    return render(request, 'pos/index.html')


def app_home(request):
    return render(request, 'apps/pos/home.html', {'app': 'pos'})
