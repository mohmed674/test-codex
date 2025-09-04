# apps/attendance/attendance_reports.py
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any, Dict, List, Tuple, cast

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils import timezone
from weasyprint import HTML  # type: ignore[import]

from apps.employees.models import Employee
from core.utils import export_to_excel

from .models import Attendance


def _apply_filters(request: HttpRequest) -> Tuple[Any, Dict[str, Any]]:
    qs = Attendance.objects.select_related("employee", "employee__department")

    employee_id = (request.GET.get("employee") or "").strip()
    department_id = (request.GET.get("department") or "").strip()
    date_from = (request.GET.get("from") or "").strip()
    date_to = (request.GET.get("to") or "").strip()

    if employee_id:
        qs = qs.filter(employee_id=employee_id)
    if department_id:
        qs = qs.filter(employee__department_id=department_id)
    if date_from and date_to:
        qs = qs.filter(date__range=[date_from, date_to])

    filters = {
        "employee": employee_id or None,
        "department": department_id or None,
        "from": date_from or None,
        "to": date_to or None,
    }
    return qs, filters


def _stats(qs: Any) -> Dict[str, int]:
    return {
        "total": qs.count() if qs else 0,
        "present": qs.filter(status="present").count() if qs else 0,
        "absent": qs.filter(status="absent").count() if qs else 0,
        "late": qs.filter(status="late").count() if qs else 0,
    }


def _fmt_date(d: Any) -> str:
    if not d:
        return "-"
    try:
        return d.strftime("%Y-%m-%d")
    except Exception:
        try:
            return timezone.localtime(d).date().strftime("%Y-%m-%d")
        except Exception:
            return str(d)


def _fmt_time(t: Any) -> str:
    if not t:
        return ""
    try:
        return t.strftime("%H:%M")
    except Exception:
        return ""


def _pick_time_field(rec: Attendance) -> Any:
    for name in ("time", "check_in", "timestamp", "entered_at"):
        if hasattr(rec, name):
            return getattr(rec, name)
    return None


def attendance_report(request: HttpRequest) -> HttpResponse:
    records, filters = _apply_filters(request)
    records = records.order_by("-date")

    context = {
        "records": records,
        "employees": Employee.objects.all(),
        "stats": _stats(records),
        "filters": filters,
    }
    return render(request, "attendance/attendance_report.html", context)


def attendance_report_pdf(request: HttpRequest) -> HttpResponse:
    records, filters = _apply_filters(request)
    template = get_template("attendance/attendance_report_pdf.html")
    html = template.render(
        {
            "records": records,
            "stats": _stats(records),
            "filters": filters,
        }
    )
    pdf_bytes: bytes = cast(bytes, HTML(string=html).write_pdf())
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="attendance_report.pdf"'
    return response


def attendance_report_excel(request: HttpRequest) -> HttpResponse:
    records, _ = _apply_filters(request)

    data: List[Dict[str, Any]] = []
    for r in records:
        # اسم الموظف
        employee_name = ""
        if getattr(r, "employee", None):
            employee_name = getattr(r.employee, "name", "") or ""

        # اسم القسم
        dept_name = ""
        if getattr(r, "employee", None) and getattr(r.employee, "department", None):
            dept_name = getattr(r.employee.department, "name", "") or ""

        # الحالة
        status_disp = getattr(r, "status", "-")
        getter = getattr(r, "get_status_display", None)
        if callable(getter):
            try:
                status_disp = getter()
            except Exception:
                status_disp = getattr(r, "status", "-")

        data.append(
            {
                "الموظف": employee_name,
                "القسم": dept_name,
                "التاريخ": _fmt_date(getattr(r, "date", None)),
                "الحالة": status_disp,
                "الوقت": _fmt_time(_pick_time_field(r)),
            }
        )

    return export_to_excel(data, filename="attendance_report.xlsx")
