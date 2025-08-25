# ERP_CORE/tracking/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from weasyprint import HTML
from django.utils import timezone
from django import forms
from core.utils import export_to_excel
from .models import ProductTracking, ProductTrackingMovement
from .forms import ProductTrackingForm
from django.db.models import F, ExpressionWrapper, fields
from django.utils import timezone
from .models import ProductTracking
from django.shortcuts import render

# ✅ تقرير متقدم: فلترة حسب المدينة، شركة الشحن، ومدة التوصيل
def advanced_tracking_report_view(request):
    records = ProductTracking.objects.all()

    # فلترة ذكية
    city_filter = request.GET.get('city')
    company_filter = request.GET.get('shipping_company')
    duration_min = request.GET.get('duration_min')
    duration_max = request.GET.get('duration_max')

    if city_filter:
        records = records.filter(notes__icontains=city_filter)

    if company_filter:
        records = records.filter(shipping_company__icontains=company_filter)

    # حساب مدة التوصيل الفعلية
    records = records.annotate(
        delivery_duration=ExpressionWrapper(
            F('delivery_date') - F('shipment_date'),
            output_field=fields.DurationField()
        )
    )

    # فلترة حسب عدد الأيام
    if duration_min:
        records = records.filter(delivery_duration__gte=f"{duration_min} days")
    if duration_max:
        records = records.filter(delivery_duration__lte=f"{duration_max} days")

    context = {
        'records': records,
        'filters': {
            'city': city_filter,
            'shipping_company': company_filter,
            'duration_min': duration_min,
            'duration_max': duration_max
        }
    }

    return render(request, 'tracking/advanced_report.html', context)


# ✅ عرض لوحة التتبع مع فلاتر
def tracking_dashboard(request):
    records = ProductTracking.objects.all()

    tracking_code = request.GET.get('tracking_code')
    customer_name = request.GET.get('customer_name')
    phone = request.GET.get('phone')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if tracking_code:
        records = records.filter(tracking_code__icontains=tracking_code)
    if customer_name:
        records = records.filter(customer_name__icontains=customer_name)
    if phone:
        records = records.filter(notes__icontains=phone)
    if date_from and date_to:
        records = records.filter(shipment_date__range=[date_from, date_to])

    records = records.order_by('-shipment_date')

    context = {
        'records': records,
        'filters': {
            'tracking_code': tracking_code,
            'customer_name': customer_name,
            'phone': phone,
            'from': date_from,
            'to': date_to,
        }
    }
    return render(request, 'tracking/dashboard.html', context)


# ✅ طباعة PDF للتقارير
def tracking_pdf(request):
    records = ProductTracking.objects.all()

    tracking_code = request.GET.get('tracking_code')
    customer_name = request.GET.get('customer_name')
    phone = request.GET.get('phone')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if tracking_code:
        records = records.filter(tracking_code__icontains=tracking_code)
    if customer_name:
        records = records.filter(customer_name__icontains=customer_name)
    if phone:
        records = records.filter(notes__icontains=phone)
    if date_from and date_to:
        records = records.filter(shipment_date__range=[date_from, date_to])

    template = get_template('tracking/tracking_pdf.html')
    html = template.render({'records': records})
    pdf_file = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="tracking_report.pdf"'
    return response


# ✅ تصدير Excel
def tracking_excel(request):
    records = ProductTracking.objects.all()

    tracking_code = request.GET.get('tracking_code')
    customer_name = request.GET.get('customer_name')
    phone = request.GET.get('phone')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if tracking_code:
        records = records.filter(tracking_code__icontains=tracking_code)
    if customer_name:
        records = records.filter(customer_name__icontains=customer_name)
    if phone:
        records = records.filter(notes__icontains=phone)
    if date_from and date_to:
        records = records.filter(shipment_date__range=[date_from, date_to])

    data = []
    for r in records:
        data.append({
            'اسم المنتج': r.product_name,
            'كود التتبع': r.tracking_code,
            'اسم العميل': r.customer_name,
            'طريقة الدفع': r.get_payment_method_display(),
            'الحالة': r.get_status_display(),
            'شركة الشحن': r.shipping_company,
            'تاريخ الشحن': r.shipment_date.strftime('%Y-%m-%d'),
            'تاريخ التسليم': r.delivery_date.strftime('%Y-%m-%d') if r.delivery_date else '',
            'ملاحظات': r.notes,
        })

    return export_to_excel(data, filename='tracking_report.xlsx')


# ✅ إدخال شحنة جديدة يدويًا
def tracking_create(request):
    if request.method == 'POST':
        form = ProductTrackingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tracking:tracking_dashboard')
    else:
        form = ProductTrackingForm()

    return render(request, 'tracking/form.html', {'form': form})


# ✅ عرض تتبع الشحنة للعميل (QR + Web)
def tracking_customer_view(request):
    tracking_code = request.GET.get('code')
    tracking_info = None
    movements = []

    if tracking_code:
        tracking_info = get_object_or_404(ProductTracking, tracking_code=tracking_code)
        movements = ProductTrackingMovement.objects.filter(
            tracking=tracking_info
        ).order_by('-timestamp')

    context = {
        'tracking': tracking_info,
        'movements': movements,
        'code': tracking_code
    }
    return render(request, 'tracking/customer_tracking.html', context)


# ✅ نقطة API ذكية للتتبع بالكود فقط (للـ App أو QR)
def tracking_api_view(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'error': 'كود التتبع مفقود'}, status=400)

    try:
        tracking = ProductTracking.objects.get(tracking_code=code)
        movements = ProductTrackingMovement.objects.filter(tracking=tracking).order_by('-timestamp')

        return JsonResponse({
            'product': tracking.product_name,
            'status': tracking.get_status_display(),
            'customer': tracking.customer_name,
            'payment_method': tracking.get_payment_method_display(),
            'shipping_company': tracking.shipping_company,
            'shipment_date': tracking.shipment_date,
            'delivery_date': tracking.delivery_date,
            'notes': tracking.notes,
            'movements': [
                {
                    'location': m.location,
                    'status': m.get_status_display(),
                    'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M'),
                    'note': m.note
                } for m in movements
            ]
        })

    except ProductTracking.DoesNotExist:
        return JsonResponse({'error': 'كود التتبع غير موجود'}, status=404)


# ✅ نموذج لإضافة حركة شحنة
class ProductTrackingMovementForm(forms.ModelForm):
    class Meta:
        model = ProductTrackingMovement
        fields = ['tracking', 'location', 'status']
        widgets = {
            'tracking': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


# ✅ عرض الحركات في لوحة مخصصة
def tracking_movement_dashboard(request):
    movements = ProductTrackingMovement.objects.select_related('tracking').all()

    code = request.GET.get('tracking_code')
    status = request.GET.get('status')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if code:
        movements = movements.filter(tracking__tracking_code__icontains=code)
    if status:
        movements = movements.filter(status=status)
    if date_from and date_to:
        movements = movements.filter(timestamp__range=[date_from, date_to])

    movements = movements.order_by('-timestamp')

    context = {
        'movements': movements,
        'filters': {
            'tracking_code': code,
            'status': status,
            'from': date_from,
            'to': date_to
        }
    }
    return render(request, 'tracking/movement_dashboard.html', context)


# ✅ إنشاء حركة جديدة
def movement_create_view(request):
    if request.method == 'POST':
        form = ProductTrackingMovementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tracking:tracking_movement_dashboard')
    else:
        form = ProductTrackingMovementForm()

    return render(request, 'tracking/movement_form.html', {'form': form})


# ✅ تقرير ذكي متقدم: تقارير حسب المدينة أو المدة أو الشركة
def advanced_tracking_report(request):
    records = ProductTracking.objects.all()

    company = request.GET.get('company')
    city = request.GET.get('city')
    delay_threshold = request.GET.get('delay')

    if company:
        records = records.filter(shipping_company__icontains=company)
    if city:
        records = records.filter(notes__icontains=city)
    if delay_threshold:
        records = records.filter(
            delivery_date__isnull=False,
            shipment_date__isnull=False
        ).extra(where=["delivery_date - shipment_date > interval %s day"], params=[delay_threshold])

    context = {
        'records': records,
        'filters': {
            'company': company,
            'city': city,
            'delay': delay_threshold
        }
    }
    return render(request, 'tracking/advanced_report.html', context)


# ✅ دالة وهمية لتفادي الخطأ
def api_track_shipment(request):
    return JsonResponse({"message": "تم الوصول إلى واجهة تتبع الشحنة بنجاح"})


from django.shortcuts import render

def index(request):
    return render(request, 'tracking/index.html')


def app_home(request):
    return render(request, 'apps/tracking/home.html', {'app': 'tracking'})
