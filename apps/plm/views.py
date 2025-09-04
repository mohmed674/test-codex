# ERP_CORE/plm/views.py
from __future__ import annotations

from typing import Any, Dict, List

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import (ChangeRequest, LifecycleStage, PLMDocument,
                     ProductLifecycle, ProductTemplate)


def _dt(v: Any) -> Any:
    return v.isoformat() if hasattr(v, "isoformat") and v else v


def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse("PLM Module Ready!")


# =========================
# 🟢 Products Endpoints
# =========================


def product_list(request: HttpRequest) -> JsonResponse:
    """إرجاع قائمة المنتجات (ProductTemplate)"""
    qs = ProductTemplate.objects.all().values(
        "id", "name", "code", "category", "uom", "active", "created_at"
    )
    data: List[Dict[str, Any]] = []
    for p in qs:
        p["created_at"] = _dt(p["created_at"])
        data.append(p)
    return JsonResponse(data, safe=False)


def product_detail(request: HttpRequest, pk: int) -> JsonResponse:
    """إرجاع تفاصيل منتج واحد"""
    product = get_object_or_404(ProductTemplate, pk=pk)
    data = {
        "id": product.pk,
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


def lifecycle_stages(request: HttpRequest) -> JsonResponse:
    """إرجاع كل المراحل المتاحة"""
    stages = list(LifecycleStage.objects.all().values("id", "name", "order"))
    return JsonResponse(stages, safe=False)


def product_lifecycle(request: HttpRequest, pk: int) -> JsonResponse:
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


def documents_list(request: HttpRequest) -> JsonResponse:
    """إرجاع المستندات كلها"""
    qs = PLMDocument.objects.all().values("id", "name", "version", "created_at")
    data: List[Dict[str, Any]] = []
    for d in qs:
        d["created_at"] = _dt(d["created_at"])
        data.append(d)
    return JsonResponse(data, safe=False)


def document_reviews(request: HttpRequest, pk: int) -> JsonResponse:
    """
    إرجاع التغييرات (Change Requests) المرتبطة بالمستند كـ "مراجعات"
    (اعتمادًا على الموديلات الحالية حيث لا يوجد DocumentReview مستقل)
    """
    crs = ChangeRequest.objects.filter(attachments=pk).values(
        "number", "status", "approved_by", "approved_at", "implemented_at", "created_at"
    )
    data: List[Dict[str, Any]] = []
    for r in crs:
        r["approved_at"] = _dt(r["approved_at"])
        r["implemented_at"] = _dt(r["implemented_at"])
        r["created_at"] = _dt(r["created_at"])
        data.append(r)
    return JsonResponse(data, safe=False)


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "plm/index.html")


def app_home(request: HttpRequest) -> HttpResponse:
    return render(request, "apps/plm/home.html", {"app": "plm"})
