# apps/employee_monitoring/views.py
"""Employee monitoring dashboards and reports.

- Replace broad try/except-pass with contextlib.suppress(...) (SIM105).
- Reduce N+1 queries in classifications via grouped annotations where possible.
- Keep dynamic field discovery for resilience across schema variations.
- Preserve functional behavior and outputs; add light typing hints & docstrings.
"""

from __future__ import annotations

from contextlib import suppress
from typing import Any, Dict, Iterable, List, Optional

from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils import timezone
from weasyprint import HTML

from apps.attendance.models import Attendance
from apps.discipline.models import DisciplineRecord
from apps.employees.models import Employee
from apps.payroll.models import Salary
from core.utils import export_to_excel

from .forms import MonitoringForm
from .models import MonitoringRecord


# ===== Helpers (تكيّف تلقائي مع أسماء الحقول/العلاقات) =====
def _field_names(model: type) -> set[str]:
    return {f.name for f in model._meta.get_fields()}


def _find_emp_fk(model: type) -> Optional[str]:
    """Return FK field name to Employee if found, else a best-effort guess."""
    for f in model._meta.get_fields():
        if getattr(f, "is_relation", False) and getattr(f, "many_to_one", False):
            with suppress(Exception):
                if f.remote_field and f.remote_field.model is Employee:
                    return f.name
    # تخمينات احتياطية
    for name in ("employee", "emp", "worker", "staff", "user"):
        if name in _field_names(model):
            return name
    return None


def _find_date_field(model: type) -> Optional[str]:
    """Find a likely date/datetime field name."""
    candidates = (
        "date",
        "created_at",
        "timestamp",
        "happened_at",
        "occurred_at",
        "day",
    )
    names = _field_names(model)
    for n in candidates:
        if n in names:
            return n
    return None


def _emp_name_path() -> str:
    """Choose a reasonable Employee display attribute."""
    names = _field_names(Employee)
    for n in ("name", "full_name", "display_name", "username", "first_name"):
        if n in names:
            return n
    return "id"


# 🔧 إدخال يدوي لمراقبة خاصة
def monitoring_input(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = MonitoringForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("employee_monitoring:monitoring_dashboard")
    else:
        form = MonitoringForm()
    return render(request, "employee_monitoring/input.html", {"form": form})


# بناء سياق اللوحة (لا يعتمد على TemplateResponse.context_data)
def _build_dashboard_context() -> Dict[str, Any]:
    """Build dashboard data with safe fallbacks and fewer queries."""
    today = timezone.now().date()

    records = (
        MonitoringRecord.objects.all().order_by("-date")
        if "date" in _field_names(MonitoringRecord)
        else MonitoringRecord.objects.all()
    )

    alerts: List[str] = []

    # إعدادات ديناميكية للحضور والانضباط
    att_emp_fk = _find_emp_fk(Attendance)
    att_date_f = _find_date_field(Attendance)
    disc_emp_fk = _find_emp_fk(DisciplineRecord)
    disc_date_f = _find_date_field(DisciplineRecord)

    emp_name_field = _emp_name_path()

    # غياب متكرر (>=3 خلال الشهر)
    with suppress(Exception):
        if att_emp_fk and att_date_f and "status" in _field_names(Attendance):
            att_abs_qs = Attendance.objects.filter(
                **{f"{att_date_f}__month": today.month},
                status="absent",
            )
            key = f"{att_emp_fk}__{emp_name_field}"
            grouped = (
                att_abs_qs.values(key).annotate(total=Count("id")).filter(total__gte=3)
            )
            for r in grouped:
                emp_label = r.get(key)
                alerts.append(f"🔴 الموظف {emp_label} غاب {r['total']} مرة هذا الشهر.")

    # تلاعب محتمل بالبصمة (تأخير أو خروج مفقود >=5)
    with suppress(Exception):
        has_exit = "exit_time" in _field_names(Attendance)
        if att_emp_fk and att_date_f:
            filt = {f"{att_date_f}__month": today.month}
            qs = Attendance.objects.filter(**filt)
            if "status" in _field_names(Attendance):
                qs = qs.filter(
                    Q(status="late") | (Q(exit_time=None) if has_exit else Q())
                )
            key = f"{att_emp_fk}__{emp_name_field}"
            grouped = qs.values(key).annotate(total=Count("id")).filter(total__gte=5)
            for m in grouped:
                emp_label = m.get(key)
                alerts.append(
                    f"⚠️ احتمال تلاعب: {emp_label} لديه {m['total']} حضور مشبوه."
                )

    # موظفون بلا أي حضور هذا الشهر
    with suppress(Exception):
        if att_emp_fk and att_date_f:
            present_ids = Attendance.objects.filter(
                **{f"{att_date_f}__month": today.month}
            ).values_list(att_emp_fk, flat=True)
            inactive = Employee.objects.exclude(id__in=list(present_ids))
            for i in inactive:
                name_val = (
                    getattr(i, emp_name_field, None)
                    or getattr(i, "get_full_name", lambda: str(i))()
                )
                alerts.append(f"🟠 الموظف {name_val} لم يسجل أي حضور هذا الشهر.")

    # ===== التصنيفات الذكية (أداء أعلى مع تجميعات مسبقة) =====
    classifications: List[Dict[str, Any]] = []

    # خرائط مسبقة لعدد الغياب/التأخير/المخالفات لكل موظف هذا الشهر
    abs_map: Dict[int, int] = {}
    late_map: Dict[int, int] = {}
    disc_map: Dict[int, int] = {}

    # Attendance aggregations
    with suppress(Exception):
        if att_emp_fk and att_date_f and "status" in _field_names(Attendance):
            month_filter = {f"{att_date_f}__month": today.month}
            # غياب
            for row in (
                Attendance.objects.filter(**month_filter, status="absent")
                .values(att_emp_fk)
                .annotate(total=Count("id"))
            ):
                emp_id = row.get(att_emp_fk)
                if emp_id is not None:
                    abs_map[int(emp_id)] = int(row["total"])
            # تأخير
            for row in (
                Attendance.objects.filter(**month_filter, status="late")
                .values(att_emp_fk)
                .annotate(total=Count("id"))
            ):
                emp_id = row.get(att_emp_fk)
                if emp_id is not None:
                    late_map[int(emp_id)] = int(row["total"])

    # Discipline aggregations
    with suppress(Exception):
        if disc_emp_fk and disc_date_f:
            for row in (
                DisciplineRecord.objects.filter(
                    **{f"{disc_date_f}__month": today.month}
                )
                .values(disc_emp_fk)
                .annotate(total=Count("id"))
            ):
                emp_id = row.get(disc_emp_fk)
                if emp_id is not None:
                    disc_map[int(emp_id)] = int(row["total"])

    # Salary probing helper (يبقى مرنًا مع اختلاف الحقول)
    def _salary_for(emp: Employee) -> Any:
        with suppress(Exception):
            s_fields = _field_names(Salary)
            sal = None
            if "month" in s_fields:
                if "employee" in s_fields:
                    sal = Salary.objects.filter(employee=emp, month=today.month).first()
                else:
                    sal = Salary.objects.filter(month=today.month).first()
            else:
                s_date_f = _find_date_field(Salary)
                if s_date_f:
                    sal = Salary.objects.filter(
                        **{f"{s_date_f}__month": today.month}
                    ).first()
            if sal:
                for amt in ("amount", "net_amount", "value", "total", "total_amount"):
                    if hasattr(sal, amt):
                        return getattr(sal, amt)
                return str(sal)
        return "-"

    for emp in Employee.objects.all():
        emp_id = int(getattr(emp, "id"))
        absences = abs_map.get(emp_id, 0)
        late = late_map.get(emp_id, 0)
        discipline_cnt = disc_map.get(emp_id, 0)
        salary_val = _salary_for(emp)

        if absences >= 3 or discipline_cnt >= 4:
            status = "⚠️ تحت المراجعة"
        elif absences == 0 and late <= 1:
            status = "✅ ملتزم"
        else:
            status = "🟡 مستقر"

        classifications.append(
            {
                "employee": emp,
                "absences": absences,
                "late": late,
                "discipline": discipline_cnt,
                "salary": salary_val,
                "status": status,
            }
        )

    return {"records": records, "alerts": alerts, "classifications": classifications}


# 🤖 لوحة المراقبة الذكية AI Monitor
def monitoring_dashboard(request: HttpRequest) -> HttpResponse:
    context = _build_dashboard_context()
    return render(request, "employee_monitoring/dashboard.html", context)


# 🖨️ PDF Report
def monitoring_report_pdf(request: HttpRequest) -> HttpResponse:
    context = _build_dashboard_context()
    try:
        tpl = get_template("employee_monitoring/monitoring_pdf.html")
        html = tpl.render(context)
    except TemplateDoesNotExist:
        # قالب بديل مبسط عند عدم توفر القالب الأصلي
        def _row(c: Dict[str, Any]) -> str:
            emp_val = getattr(c["employee"], _emp_name_path(), c["employee"])
            return (
                "<tr>"
                f"<td>{emp_val}</td>"
                f"<td>{c['absences']}</td>"
                f"<td>{c['late']}</td>"
                f"<td>{c['discipline']}</td>"
                f"<td>{c['salary']}</td>"
                f"<td>{c['status']}</td>"
                "</tr>"
            )

        rows = "".join(_row(c) for c in context.get("classifications", []))
        html = (
            "<html><head><meta charset='utf-8'>"
            "<style>"
            "body{font-family:'DejaVu Sans',Arial;} "
            "table{width:100%;border-collapse:collapse} "
            "th,td{border:1px solid #999;padding:6px;font-size:12px;text-align:center}"
            "</style></head><body>"
            "<h3>AI Monitor Report</h3>"
            "<table>"
            "<thead>"
            "<tr>"
            "<th>الموظف</th><th>الغياب</th><th>التأخير</th>"
            "<th>مخالفات</th><th>المرتب</th><th>التصنيف</th>"
            "</tr>"
            "</thead>"
            f"<tbody>{rows}</tbody>"
            "</table>"
            "</body></html>"
        )
    pdf_file = HTML(string=html).write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'filename="ai_monitor_report.pdf"'
    return response


# 📊 Excel Report
def monitoring_report_excel(request: HttpRequest) -> HttpResponse:
    context = _build_dashboard_context()
    data: List[Dict[str, Any]] = []
    name_field = _emp_name_path()
    for c in context.get("classifications", []):
        emp = c["employee"]
        emp_name = (
            getattr(emp, name_field, None)
            or getattr(emp, "get_full_name", lambda: str(emp))()
        )
        data.append(
            {
                "الموظف": emp_name,
                "الغياب": c["absences"],
                "التأخير": c["late"],
                "مخالفات": c["discipline"],
                "المرتب": c["salary"],
                "التصنيف": c["status"],
            }
        )
    return export_to_excel(data, filename="ai_monitor_report.xlsx")


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "employee_monitoring/index.html")


def app_home(request: HttpRequest) -> HttpResponse:
    return render(
        request, "apps/employee_monitoring/home.html", {"app": "employee_monitoring"}
    )
