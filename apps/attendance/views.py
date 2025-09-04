# apps/attendance/views.py
from __future__ import annotations

from contextlib import suppress
from datetime import datetime
from typing import Any, Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.attendance.exports.attendance_exports import \
    export_attendance_excel  # noqa: F401
from apps.attendance.exports.attendance_exports import \
    export_attendance_pdf  # noqa: F401
from apps.attendance.exports.attendance_exports import \
    export_lateness_absence_excel  # noqa: F401
from apps.evaluation.models import LatenessAbsence

from .forms import AttendanceForm

try:
    from .models import Attendance
except Exception:  # احتياطي لبيئات التحليل الساكن
    from django.apps import apps as django_apps

    Attendance = django_apps.get_model("attendance", "Attendance")  # type: ignore[assignment]


def _safe_select_related():
    qs = Attendance.objects.all()
    with suppress(Exception):
        return qs.select_related("evaluation__employee")
    with suppress(Exception):
        return qs.select_related("employee")
    return qs


def _export_pdf(
    qs: Any, template_path: Optional[str] = None, filename: Optional[str] = None
) -> HttpResponse:
    """
    غلاف آمن يدعم تمريـر template_path/filename إن كانت مدعومة،
    ويعود للتوقيع القديم عند عدم دعم المعاملات.
    """
    with suppress(TypeError):  # ✅ SIM105
        if template_path or filename:
            return export_attendance_pdf(
                qs,
                template_path=template_path or "attendance/attendance_pdf.html",
                filename=filename or "attendance.pdf",
            )
    return export_attendance_pdf(qs)


def attendance_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("attendance_list")
    else:
        form = AttendanceForm()
    return render(request, "attendance/input.html", {"form": form})


def attendance_list(request: HttpRequest) -> HttpResponse:
    name = request.GET.get("name", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    status = request.GET.get("status", "").strip()

    records = _safe_select_related()

    if name:
        records = records.filter(evaluation__employee__name__icontains=name)
    if date_from:
        with suppress(ValueError):  # ✅ SIM105
            records = records.filter(
                date__gte=datetime.strptime(date_from, "%Y-%m-%d").date()
            )
    if date_to:
        with suppress(ValueError):  # ✅ SIM105
            records = records.filter(
                date__lte=datetime.strptime(date_to, "%Y-%m-%d").date()
            )
    if status:
        records = records.filter(status=status)

    if request.GET.get("export") == "excel":
        return export_attendance_excel(records)
    if request.GET.get("export") == "pdf":
        return _export_pdf(records)

    return render(request, "attendance/attendance_list.html", {"records": records})


def lateness_absence_list(request: HttpRequest) -> HttpResponse:
    name = request.GET.get("name", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    status = request.GET.get("status", "").strip()

    entries = LatenessAbsence.objects.select_related("evaluation__employee").all()

    if name:
        entries = entries.filter(evaluation__employee__name__icontains=name)
    if date_from:
        with suppress(ValueError):  # ✅ SIM105
            entries = entries.filter(
                date__gte=datetime.strptime(date_from, "%Y-%m-%d").date()
            )
    if date_to:
        with suppress(ValueError):  # ✅ SIM105
            entries = entries.filter(
                date__lte=datetime.strptime(date_to, "%Y-%m-%d").date()
            )
    if status:
        entries = entries.filter(status=status)

    if request.GET.get("export") == "excel":
        return export_lateness_absence_excel(entries)
    if request.GET.get("export") == "pdf":
        return _export_pdf(
            entries,
            template_path="attendance/lateness_absence_pdf.html",
            filename="lateness_absence.pdf",
        )
    if request.GET.get("export") == "print":
        return render(
            request, "attendance/lateness_absence_print.html", {"entries": entries}
        )

    return render(
        request, "attendance/lateness_absence_list.html", {"entries": entries}
    )


def attendance_print_view(request: HttpRequest) -> HttpResponse:
    name = request.GET.get("name", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    status = request.GET.get("status", "").strip()

    records = _safe_select_related()

    if name:
        records = records.filter(evaluation__employee__name__icontains=name)
    if date_from:
        with suppress(ValueError):  # ✅ SIM105
            records = records.filter(
                date__gte=datetime.strptime(date_from, "%Y-%m-%d").date()
            )
    if date_to:
        with suppress(ValueError):  # ✅ SIM105
            records = records.filter(
                date__lte=datetime.strptime(date_to, "%Y-%m-%d").date()
            )
    if status:
        records = records.filter(status=status)

    return render(request, "attendance/attendance_print.html", {"records": records})


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "attendance/index.html")


def app_home(request: HttpRequest) -> HttpResponse:
    return render(request, "apps/attendance/home.html", {"app": "attendance"})
