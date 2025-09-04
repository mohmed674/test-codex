# ERP_CORE/evaluation/report_views.py
from __future__ import annotations

from typing import Any, Dict, List

from django.shortcuts import render
from django.utils.dateparse import parse_date

from core.utils import export_to_excel, render_to_pdf

from .models import Evaluation


def _fmt_date(v: Any) -> str:
    """Safe date formatting helper (avoids optional member access warnings)."""
    if not v:
        return ""
    try:
        return v.strftime("%Y-%m-%d")  # type: ignore[call-arg]
    except Exception:
        return ""


def evaluation_report_view(request):
    records = Evaluation.objects.select_related("employee").all()

    name = request.GET.get("name")
    eval_type = request.GET.get("eval_type")
    evaluator = request.GET.get("evaluator")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if name:
        records = records.filter(employee__name__icontains=name)
    if eval_type:
        records = records.filter(eval_type__icontains=eval_type)
    if evaluator:
        records = records.filter(evaluator__icontains=evaluator)
    if date_from:
        records = records.filter(date__gte=parse_date(str(date_from)))
    if date_to:
        records = records.filter(date__lte=parse_date(str(date_to)))

    if request.GET.get("export") == "1":
        export_data: List[Dict[str, Any]] = [
            {
                "اسم الموظف": (
                    getattr(r.employee, "name", "")
                    if getattr(r, "employee", None)
                    else ""
                ),
                "نوع التقييم": getattr(r, "eval_type", ""),
                "المقيِّم": getattr(r, "evaluator", ""),
                "النتيجة": getattr(r, "score", ""),
                "الملاحظات": getattr(r, "notes", ""),
                "التاريخ": _fmt_date(getattr(r, "date", None)),
            }
            for r in records
        ]
        return export_to_excel(export_data, "evaluation_report.xlsx")

    if request.GET.get("download_pdf") == "1":
        context = {"records": records, "request": request}
        return render_to_pdf("evaluation/pdf_template.html", context)

    return render(
        request,
        "evaluation/behavior_reports.html",
        {"records": records, "request": request},
    )
