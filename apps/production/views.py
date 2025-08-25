from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Sum
from core.utils import render_to_pdf, export_to_excel
from .models import ProductionOrder, MaterialConsumption, QualityCheck, ProductVersion
from .forms import ProductionOrderForm, MaterialConsumptionForm, QualityCheckForm, ProductVersionForm
from apps.employee_monitoring.models import MonitoringRecord



# ✅ تسجيل دخول قسم الإنتاج في سجل المراقبة
def add_production(request):
    if request.method == 'POST':
        # تأكد أن لديك علاقة بين User و Employee
        MonitoringRecord.objects.create(
            employee=request.user.employee,  # عدل إذا لم يكن لديك علاقة مباشرة
            status='present',
            notes='دخول لقسم الإنتاج عبر النظام',
            date=timezone.now()
        )
        return render(request, 'success.html')
    return render(request, 'production/production_form.html')

# ✅ لوحة تحكم الإنتاج
def production_dashboard_view(request):
    total_orders = ProductionOrder.objects.count()
    total_quantity = ProductionOrder.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_consumptions = MaterialConsumption.objects.count()
    return render(request, 'production/production_dashboard.html', {
        'total_orders': total_orders,
        'total_quantity': total_quantity,
        'total_consumptions': total_consumptions
    })

# ✅ عرض أوامر الإنتاج
def order_list_view(request):
    orders = ProductionOrder.objects.select_related('product').all()

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf("production/order_pdf.html", {"orders": orders, "request": request})

    if request.GET.get("export") == "1":
        data = [{
            "الكود": o.order_number,
            "المنتج": o.product.name,
            "الكمية": o.quantity,
            "الحالة": o.status,
            "الملاحظات": o.notes,
            "التاريخ": o.created_at.strftime("%Y-%m-%d"),
        } for o in orders]
        return export_to_excel(data, filename="production_orders.xlsx")

    return render(request, 'production/order_list.html', {'orders': orders})

# ✅ إضافة أمر إنتاج
def order_create_view(request):
    if request.method == 'POST':
        form = ProductionOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            return redirect('production:order_list')
    else:
        form = ProductionOrderForm()
    return render(request, 'production/order_form.html', {'form': form})

# ✅ عرض استهلاك الخامات
def consumption_list_view(request):
    consumptions = MaterialConsumption.objects.select_related('order', 'material').all()

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf("production/consumption_pdf.html", {"consumptions": consumptions, "request": request})

    if request.GET.get("export") == "1":
        data = [{
            "الكود": c.order.order_number,
            "الخام": c.material.name,
            "الكمية": c.quantity_used,
            "الهالك": c.wastage,
        } for c in consumptions]
        return export_to_excel(data, filename="material_consumptions.xlsx")

    return render(request, 'production/consumption_list.html', {'consumptions': consumptions})

# ✅ إضافة استهلاك خام
def consumption_create_view(request):
    if request.method == 'POST':
        form = MaterialConsumptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('production:consumption_list')
    else:
        form = MaterialConsumptionForm()
    return render(request, 'production/consumption_form.html', {'form': form})

# ✅ عرض فحوصات الجودة
def quality_check_list_view(request):
    checks = QualityCheck.objects.select_related('product', 'order', 'stage', 'inspector').all()

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf("production/quality_check_pdf.html", {"checks": checks, "request": request})

    if request.GET.get("export") == "1":
        data = [{
            "المنتج": q.product.name,
            "المرحلة": q.stage.stage_name,
            "أمر التشغيل": q.order.order_number,
            "المفتش": q.inspector.name if q.inspector else "-",
            "الحالة": dict(q._meta.get_field("status").choices).get(q.status),
            "التاريخ": q.inspected_at.strftime("%Y-%m-%d %H:%M"),
            "ملاحظات": q.notes or "",
        } for q in checks]
        return export_to_excel(data, filename="quality_checks.xlsx")

    return render(request, 'production/quality_check_list.html', {'checks': checks})

# ✅ إضافة فحص جودة جديد
def quality_check_create_view(request):
    if request.method == 'POST':
        form = QualityCheckForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('production:quality_check_list')
    else:
        form = QualityCheckForm()
    return render(request, 'production/quality_check_form.html', {'form': form})

# ✅ PLM - عرض نسخ المنتج
def product_version_list_view(request):
    versions = ProductVersion.objects.select_related('product', 'created_by').all()

    if request.GET.get("export") == "1":
        data = [{
            "المنتج": v.product.name,
            "الكود": v.version_code,
            "الموسم": v.season,
            "الوصف": getattr(v, 'description', ''),  # إذا كان الحقل موجودًا
            "المستخدم": v.created_by.username if v.created_by else "-",
            "مفعل": "نعم" if v.is_active else "لا",
        } for v in versions]
        return export_to_excel(data, filename="product_versions.xlsx")

    return render(request, 'production/product_version_list.html', {'versions': versions})

# ✅ PLM - إضافة نسخة منتج جديدة
def product_version_create_view(request):
    if request.method == 'POST':
        form = ProductVersionForm(request.POST)
        if form.is_valid():
            version = form.save(commit=False)
            version.created_by = request.user
            version.save()
            return redirect('production:product_version_list')
    else:
        form = ProductVersionForm()
    return render(request, 'production/product_version_form.html', {'form': form})


from django.shortcuts import render

def index(request):
    return render(request, 'production/index.html')


def app_home(request):
    return render(request, 'apps/production/home.html', {'app': 'production'})
