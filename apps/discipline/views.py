from __future__ import annotations

import datetime
from typing import Optional

import openpyxl
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from openpyxl.worksheet.worksheet import Worksheet
from weasyprint import HTML

from apps.discipline.models import DisciplineRecord
from apps.employees.models import Employee


def _parse_date(s: str) -> Optional[datetime.date]:
    s = (s or "").strip()
    if not s:
        return None
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def discipline_list(request: HttpRequest) -> HttpResponse:
    """
    عرض قائمة بكل عقوبات الموظفين مع إمكانية التصفية.
    """
    records = (
        DisciplineRecord.objects.select_related("employee").all().order_by("-date")
    )

    employee_id = request.GET.get("employee_id")
    if employee_id:
        try:
            records = records.filter(employee_id=int(employee_id))
        except (TypeError, ValueError):
            pass

    date_from = _parse_date(request.GET.get("date_from", ""))
    date_to = _parse_date(request.GET.get("date_to", ""))

    if date_from:
        records = records.filter(date__gte=date_from)
    if date_to:
        records = records.filter(date__lte=date_to)

    return render(
        request,
        "discipline/discipline_list.html",
        {
            "records": records,
            "employee_id": employee_id or "",
            "date_from": date_from.isoformat() if date_from else "",
            "date_to": date_to.isoformat() if date_to else "",
        },
    )


def employee_discipline_history(request: HttpRequest, employee_id: int) -> HttpResponse:
    """
    عرض سجل عقوبات موظف معيّن مع التصدير إلى PDF وExcel.
    """
    employee = get_object_or_404(Employee, pk=employee_id)

    date_from = _parse_date(request.GET.get("date_from", ""))
    date_to = _parse_date(request.GET.get("date_to", ""))

    records = DisciplineRecord.objects.filter(employee=employee)
    if date_from:
        records = records.filter(date__gte=date_from)
    if date_to:
        records = records.filter(date__lte=date_to)

    # ✅ تصدير Excel
    if request.GET.get("export") == "1":
        wb = openpyxl.Workbook()
        ws: Worksheet = wb.active or wb.create_sheet(title="Sheet1")
        ws.title = "Employee Discipline"
        ws.append(["نوع الإجراء", "القيمة", "السبب", "أنشئ بواسطة", "التاريخ"])

        for r in records:
            r_date_str = (
                r.date.strftime("%Y-%m-%d") if hasattr(r.date, "strftime") else ""
            )
            ws.append(
                [
                    r.type,
                    str(r.value) if r.value is not None else "-",
                    r.reason if r.reason is not None else "-",
                    str(r.created_by) if r.created_by is not None else "-",
                    r_date_str,
                ]
            )

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f"attachment; filename=discipline_{employee.pk}.xlsx"
        )
        wb.save(response)
        return response

    # ✅ تصدير PDF
    if request.GET.get("download_pdf") == "1":
        html_string: str = render_to_string(
            "discipline/employee_discipline_history.html",
            {
                "employee": employee,
                "records": records,
                "request": request,
                "date_from": date_from.isoformat() if date_from else "",
                "date_to": date_to.isoformat() if date_to else "",
            },
        )
        pdf_bytes = HTML(string=html_string).write_pdf() or b""
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'inline; filename="discipline_{employee.pk}.pdf"'
        )
        return response

    return render(
        request,
        "discipline/employee_discipline_history.html",
        {
            "employee": employee,
            "records": records,
            "date_from": date_from.isoformat() if date_from else "",
            "date_to": date_to.isoformat() if date_to else "",
        },
    )


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "discipline/index.html")


def app_home(request: HttpRequest) -> HttpResponse:
    return render(request, "apps/discipline/home.html", {"app": "discipline"})
