# ERP_CORE/evaluation/report_views.py

from django.shortcuts import render
from django.http import HttpResponse
from .models import Evaluation
from django.db.models import Q
from django.utils.dateparse import parse_date
from core.utils import export_to_excel, render_to_pdf


def evaluation_report_view(request):
    records = Evaluation.objects.select_related('employee').all()

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
        records = records.filter(date__gte=parse_date(date_from))
    if date_to:
        records = records.filter(date__lte=parse_date(date_to))

    if request.GET.get("export") == "1":
        export_data = [
            {
                "اسم الموظف": r.employee.name,
                "نوع التقييم": r.eval_type,
                "المقيِّم": r.evaluator,
                "النتيجة": r.score,
                "الملاحظات": r.notes,
                "التاريخ": r.date.strftime("%Y-%m-%d")
            } for r in records
        ]
        return export_to_excel(export_data, "evaluation_report.xlsx")

    if request.GET.get("download_pdf") == "1":
        context = {
            "records": records,
            "request": request
        }
        return render_to_pdf("evaluation/pdf_template.html", context)

    return render(request, "evaluation/behavior_reports.html", {
        "records": records,
        "request": request
    })
