# apps/production/views.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.employee_monitoring.models import MonitoringRecord
from core.utils import export_to_excel, render_to_pdf

from .forms import (MaterialConsumptionForm, ProductionOrderForm,
                    ProductVersionForm, QualityCheckForm)
from .models import (MaterialConsumption, ProductionOrder, ProductVersion,
                     QualityCheck)


# ===== Helpers =====
def _safe_choice_label(obj: Any, field_name: str, value: Any) -> str:
    """
    Return human-readable label for a field with choices. Works even if the
    field/choices are missing or key types mismatch (bytes/str/int).
    """
    try:
        field = obj._meta.get_field(field_name)
        choices: Sequence[Tuple[Any, Any]] = getattr(field, "choices", ()) or ()
        mapping: Dict[str, str] = {str(k): str(v) for k, v in choices}
        return mapping.get(str(value), str(value))
    except Exception:
        return str(value)


def _safe_dt(dt: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M") -> str:
    return dt.strftime(fmt) if isinstance(dt, datetime) else ""


def _user_label(u: Any) -> str:
    """
    Return a robust label for user/employee objects.
    Tries username, name, full_name, then str(u).
    """
    for attr in ("username", "name", "full_name", "display_name"):
        if hasattr(u, attr):
            val = getattr(u, attr)
            if val:
                return str(val)
    return str(u) if u is not None else "-"


# ✅ تسجيل دخول قسم الإنتاج في سجل المراقبة
def add_production(request):
    if request.method == "POST":
        MonitoringRecord.objects.create(
            employee=getattr(request.user, "employee", None),
            status="present",
            notes="دخول لقسم الإنتاج عبر النظام",
            date=timezone.now(),
        )
        return render(request, "success.html")
    return render(request, "production/production_form.html")


# ✅ لوحة تحكم الإنتاج
def production_dashboard_view(request):
    total_orders = ProductionOrder.objects.count()
    total_quantity = (
        ProductionOrder.objects.aggregate(Sum("quantity"))["quantity__sum"] or 0
    )
    total_consumptions = MaterialConsumption.objects.count()
    return render(
        request,
        "production/production_dashboard.html",
        {
            "total_orders": total_orders,
            "total_quantity": total_quantity,
            "total_consumptions": total_consumptions,
        },
    )


# ✅ عرض أوامر الإنتاج
def order_list_view(request):
    orders = ProductionOrder.objects.select_related("product").all()

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf(
            "production/order_pdf.html", {"orders": orders, "request": request}
        )

    if request.GET.get("export") == "1":
        data = []
        for o in orders:
            dt = getattr(o, "created_at", None)
            created_str = dt.strftime("%Y-%m-%d") if isinstance(dt, datetime) else ""
            data.append(
                {
                    "الكود": o.order_number,
                    "المنتج": getattr(o.product, "name", ""),
                    "الكمية": o.quantity,
                    "الحالة": o.status,
                    "الملاحظات": o.notes,
                    "التاريخ": created_str,
                }
            )
        return export_to_excel(data, filename="production_orders.xlsx")

    return render(request, "production/order_list.html", {"orders": orders})


# ✅ إضافة أمر إنتاج
def order_create_view(request):
    if request.method == "POST":
        form = ProductionOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = (
                request.user
                if getattr(request.user, "is_authenticated", False)
                else None
            )
            order.save()
            return redirect("production:order_list")
    else:
        form = ProductionOrderForm()
    return render(request, "production/order_form.html", {"form": form})


# ✅ عرض استهلاك الخامات
def consumption_list_view(request):
    consumptions = MaterialConsumption.objects.select_related("order", "material").all()

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf(
            "production/consumption_pdf.html",
            {"consumptions": consumptions, "request": request},
        )

    if request.GET.get("export") == "1":
        data = [
            {
                "الكود": getattr(c.order, "order_number", ""),
                "الخام": getattr(c.material, "name", ""),
                "الكمية": c.quantity_used,
                "الهالك": getattr(c, "wastage", 0),
            }
            for c in consumptions
        ]
        return export_to_excel(data, filename="material_consumptions.xlsx")

    return render(
        request, "production/consumption_list.html", {"consumptions": consumptions}
    )


# ✅ إضافة استهلاك خام
def consumption_create_view(request):
    if request.method == "POST":
        form = MaterialConsumptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("production:consumption_list")
    else:
        form = MaterialConsumptionForm()
    return render(request, "production/consumption_form.html", {"form": form})


# ✅ عرض فحوصات الجودة
def quality_check_list_view(request):
    checks = QualityCheck.objects.select_related(
        "product", "order", "stage", "inspector"
    ).all()

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf(
            "production/quality_check_pdf.html", {"checks": checks, "request": request}
        )

    if request.GET.get("export") == "1":
        data = [
            {
                "المنتج": getattr(q.product, "name", ""),
                "المرحلة": getattr(q.stage, "stage_name", ""),
                "أمر التشغيل": getattr(q.order, "order_number", ""),
                "المفتش": (
                    _user_label(q.inspector) if getattr(q, "inspector", None) else "-"
                ),
                "الحالة": _safe_choice_label(q, "status", getattr(q, "status", "")),
                "التاريخ": _safe_dt(getattr(q, "inspected_at", None)),
                "ملاحظات": q.notes or "",
            }
            for q in checks
        ]
        return export_to_excel(data, filename="quality_checks.xlsx")

    return render(request, "production/quality_check_list.html", {"checks": checks})


# ✅ إضافة فحص جودة جديد
def quality_check_create_view(request):
    if request.method == "POST":
        form = QualityCheckForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("production:quality_check_list")
    else:
        form = QualityCheckForm()
    return render(request, "production/quality_check_form.html", {"form": form})


# ✅ PLM - عرض نسخ المنتج
def product_version_list_view(request):
    versions = ProductVersion.objects.select_related("product", "created_by").all()

    if request.GET.get("export") == "1":
        data = [
            {
                "المنتج": getattr(v.product, "name", ""),
                "الكود": v.version_code,
                "الموسم": v.season,
                "الوصف": getattr(v, "description", ""),
                "المستخدم": (
                    _user_label(v.created_by) if getattr(v, "created_by", None) else "-"
                ),
                "مفعل": "نعم" if v.is_active else "لا",
            }
            for v in versions
        ]
        return export_to_excel(data, filename="product_versions.xlsx")

    return render(
        request, "production/product_version_list.html", {"versions": versions}
    )


# ✅ PLM - إضافة نسخة منتج جديدة
def product_version_create_view(request):
    if request.method == "POST":
        form = ProductVersionForm(request.POST)
        if form.is_valid():
            version = form.save(commit=False)
            version.created_by = (
                request.user
                if getattr(request.user, "is_authenticated", False)
                else None
            )
            version.save()
            return redirect("production:product_version_list")
    else:
        form = ProductVersionForm()
    return render(request, "production/product_version_form.html", {"form": form})


def index(request):
    return render(request, "production/index.html")


def app_home(request):
    return render(request, "apps/production/home.html", {"app": "production"})
