from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .models import (
    ProductTemplate,
    ProductLifecycle,
    LifecycleStage,
    PLMDocument,
    ChangeRequest,
)

def _dt(v):
    return v.isoformat() if hasattr(v, "isoformat") and v else v

def home(request):
    return HttpResponse("PLM Module Ready!")

# =========================
# 🟢 Products Endpoints
# =========================

def product_list(request):
    """إرجاع قائمة المنتجات (ProductTemplate)"""
    qs = ProductTemplate.objects.all().values(
        "id", "name", "code", "category", "uom", "active", "created_at"
    )
    data = []
    for p in qs:
        p["created_at"] = _dt(p["created_at"])
        data.append(p)
    return JsonResponse(data, safe=False)

def product_detail(request, pk):
    """إرجاع تفاصيل منتج واحد"""
    product = get_object_or_404(ProductTemplate, pk=pk)
    data = {
        "id": product.id,
        "name": product.name,
        "code": product.code,
        "category": product.category,
        "uom": product.uom,
        "active": product.active,
        "description": product.description,
        "created_at": _dt(product.created_at),
    }
    return JsonResponse(data)

# =========================
# 🟢 Lifecycle Endpoints
# =========================

def lifecycle_stages(request):
    """إرجاع كل المراحل المتاحة"""
    stages = list(
        LifecycleStage.objects.all().values("id", "name", "order")
    )
    return JsonResponse(stages, safe=False)

def product_lifecycle(request, pk):
    """إرجاع دورة حياة منتج معين"""
    lifecycles = ProductLifecycle.objects.filter(product_id=pk).select_related("stage")
    data = [
        {
            "stage": lc.stage.name,
            "started_at": _dt(lc.started_at),
            "ended_at": _dt(lc.ended_at),
        }
        for lc in lifecycles
    ]
    return JsonResponse(data, safe=False)

# =========================
# 🟢 Documents & Related Changes
# =========================

def documents_list(request):
    """إرجاع المستندات كلها"""
    qs = PLMDocument.objects.all().values("id", "name", "version", "created_at")
    data = []
    for d in qs:
        d["created_at"] = _dt(d["created_at"])
        data.append(d)
    return JsonResponse(data, safe=False)

def document_reviews(request, pk):
    """
    إرجاع التغييرات (Change Requests) المرتبطة بالمستند كـ "مراجعات"
    (اعتمادًا على الموديلات الحالية حيث لا يوجد DocumentReview مستقل)
    """
    crs = ChangeRequest.objects.filter(attachments=pk).values(
        "number", "status", "approved_by", "approved_at", "implemented_at", "created_at"
    )
    data = []
    for r in crs:
        r["approved_at"] = _dt(r["approved_at"])
        r["implemented_at"] = _dt(r["implemented_at"])
        r["created_at"] = _dt(r["created_at"])
        data.append(r)
    return JsonResponse(data, safe=False)


from django.shortcuts import render

def index(request):
    return render(request, 'plm/index.html')


def app_home(request):
    return render(request, 'apps/plm/home.html', {'app': 'plm'})
