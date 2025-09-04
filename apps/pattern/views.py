# ERP_CORE/pattern/views.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.utils import export_to_excel, render_to_pdf

from .forms import PatternDesignForm, PatternExecutionForm, PatternPieceForm
from .models import PatternDesign, PatternExecution, PatternPiece

# ---- Helpers ---------------------------------------------------------------


def _safe_get(obj: Any, attr: str, default: Any = "") -> Any:
    return getattr(obj, attr, default)


def _safe_dt(dt: Any, fmt: str = "%Y-%m-%d %H:%M") -> str:
    return dt.strftime(fmt) if isinstance(dt, datetime) else ""


# ✅ لوحة التحكم
@login_required
def pattern_dashboard(request):
    total_designs = PatternDesign.objects.count()
    total_executions = PatternExecution.objects.count()
    return render(
        request,
        "pattern/dashboard.html",
        {
            "total_designs": total_designs,
            "total_executions": total_executions,
        },
    )


# ✅ عرض التصاميم
@login_required
def design_list_view(request):
    designs = PatternDesign.objects.all()

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf(
            "pattern/designs_pdf.html", {"designs": designs, "request": request}
        )

    if request.GET.get("export") == "1":
        data: List[Dict[str, Any]] = []
        for d in designs:
            data.append(
                {
                    "العنوان": _safe_get(d, "title", ""),
                    "التصنيف": _safe_get(d, "category", ""),
                    "الوصف": _safe_get(d, "description", ""),
                    "التاريخ": _safe_dt(_safe_get(d, "created_at", None), "%Y-%m-%d"),
                }
            )
        return export_to_excel(data, filename="pattern_designs.xlsx")

    return render(request, "pattern/design_list.html", {"designs": designs})


# ✅ إضافة تصميم
@login_required
def design_create_view(request):
    if request.method == "POST":
        form = PatternDesignForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            return redirect("pattern:design_list")
    else:
        form = PatternDesignForm()
    return render(request, "pattern/design_form.html", {"form": form})


# ✅ إدارة القطع
@login_required
def piece_list_view(request, design_id: int):
    design = get_object_or_404(PatternDesign, id=design_id)
    pieces = PatternPiece.objects.filter(design=design)
    return render(
        request, "pattern/piece_list.html", {"design": design, "pieces": pieces}
    )


@login_required
def piece_create_view(request, design_id: int):
    design = get_object_or_404(PatternDesign, id=design_id)
    if request.method == "POST":
        form = PatternPieceForm(request.POST)
        if form.is_valid():
            piece = form.save(commit=False)
            piece.design = design
            piece.save()
            return redirect("pattern:piece_list", design_id=design.pk)
    else:
        form = PatternPieceForm()
    return render(request, "pattern/piece_form.html", {"form": form, "design": design})


# ✅ تنفيذ باترون
@login_required
def execution_list_view(request):
    executions = PatternExecution.objects.select_related(
        "design", "executed_by", "production_order"
    ).all()

    if request.GET.get("download_pdf") == "1":
        return render_to_pdf(
            "pattern/executions_pdf.html",
            {"executions": executions, "request": request},
        )

    if request.GET.get("export") == "1":
        data: List[Dict[str, Any]] = []
        for e in executions:
            design = _safe_get(e, "design", None)
            po = _safe_get(e, "production_order", None)
            data.append(
                {
                    "الباترون": _safe_get(design, "title", "") if design else "",
                    "نوع التنفيذ": _safe_get(e, "execution_type", ""),
                    "أمر الإنتاج": _safe_get(po, "order_number", "") if po else "",
                    "المنفذ": str(_safe_get(e, "executed_by", "")),
                    "التاريخ": _safe_dt(_safe_get(e, "executed_at", None)),
                }
            )
        return export_to_excel(data, filename="pattern_executions.xlsx")

    return render(request, "pattern/execution_list.html", {"executions": executions})


@login_required
def execution_create_view(request):
    if request.method == "POST":
        form = PatternExecutionForm(request.POST)
        if form.is_valid():
            execution = form.save(commit=False)
            execution.executed_by = request.user
            execution.executed_at = timezone.now()
            execution.save()
            return redirect("pattern:execution_list")
    else:
        form = PatternExecutionForm()
    return render(request, "pattern/execution_form.html", {"form": form})


def index(request):
    return render(request, "pattern/index.html")


def app_home(request):
    return render(request, "apps/pattern/home.html", {"app": "pattern"})
