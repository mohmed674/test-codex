# apps/payroll/views.py

from __future__ import annotations

import csv
import os
import tempfile
from datetime import datetime

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template, render_to_string
from weasyprint import HTML

from apps.employees.models import Employee

from .forms import AdvanceForm, PolicySettingFormSet
from .models import Advance, PaymentRecord, Salary


def advance_list(request: HttpRequest) -> HttpResponse:
    advances = Advance.objects.select_related("employee").all()
    name = request.GET.get("name")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    advance_type = request.GET.get("type")

    if name:
        advances = advances.filter(employee__name__icontains=name)
    if date_from:
        advances = advances.filter(date__gte=date_from)
    if date_to:
        advances = advances.filter(date__lte=date_to)
    if advance_type:
        advances = advances.filter(type=advance_type)

    advances = advances.order_by("-date")

    if "export" in request.GET:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="advances.csv"'
        writer = csv.writer(response)
        writer.writerow(["الموظف", "المبلغ", "النوع", "التاريخ", "ملاحظة"])
        for a in advances:
            writer.writerow([a.employee.name, a.amount, a.type, a.date, a.note])
        return response

    if "download_pdf" in request.GET:
        template_path = "payroll/advances_pdf.html"
        context = {"advances": advances}
        html_string = get_template(template_path).render(context)
        with tempfile.NamedTemporaryFile(delete=True) as output:
            HTML(string=html_string).write_pdf(output.name)
            output.seek(0)
            response = HttpResponse(output.read(), content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="advances.pdf"'
            return response

    return render(request, "payroll/advance_list.html", {"advances": advances})


def add_advance(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AdvanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("advance_list")
    else:
        form = AdvanceForm()
    return render(request, "payroll/add_advance.html", {"form": form})


def calculate_daily_payment(request: HttpRequest, employee_id: int) -> JsonResponse:
    employee = get_object_or_404(Employee, id=employee_id)
    date_str = request.GET.get("date")
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid date format"}, status=400)

    payment = PaymentRecord.objects.filter(
        employee=employee, date=date_obj, type="daily"
    ).first()
    if payment:
        return JsonResponse({"daily_amount": float(payment.amount)})
    return JsonResponse({"daily_amount": 0})


def salary_list(request: HttpRequest) -> HttpResponse:
    salaries = Salary.objects.select_related("employee").all()
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    employee_name = request.GET.get("employee")
    download_pdf = request.GET.get("download_pdf")

    if from_date:
        salaries = salaries.filter(created_at__date__gte=from_date)
    if to_date:
        salaries = salaries.filter(created_at__date__lte=to_date)
    if employee_name:
        salaries = salaries.filter(employee__name__icontains=employee_name)

    salaries = salaries.order_by("-created_at")

    if download_pdf:
        html_string = render_to_string(
            "payroll/salary_pdf_report.html",
            {
                "salaries": salaries,
                "filter_date": f"{from_date or 'من البداية'} إلى {to_date or 'الآن'}",
                "generated_at": datetime.now(),
            },
        )
        result = tempfile.NamedTemporaryFile(delete=True, suffix=".pdf")
        HTML(string=html_string).write_pdf(result.name)
        with open(result.name, "rb") as pdf:
            response = HttpResponse(pdf.read(), content_type="application/pdf")
            response["Content-Disposition"] = 'inline; filename="salary_report.pdf"'
            return response

    return render(request, "payroll/salary_list.html", {"salaries": salaries})


def add_salary(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        employee_id = request.POST.get("employee")
        base_salary = float(request.POST.get("base_salary", 0))
        production_bonus = float(request.POST.get("production_bonus", 0))
        deductions = float(request.POST.get("deductions", 0))
        note = request.POST.get("note", "")
        employee = get_object_or_404(Employee, id=employee_id)

        final_salary = base_salary + production_bonus - deductions

        now = datetime.now()
        salary = Salary.objects.create(
            employee=employee,
            month=now.month,
            year=now.year,
            base_salary=base_salary,
            production_bonus=production_bonus,
            deductions=deductions,
            final_salary=final_salary,
        )

        salary_id: int = salary.pk or 0
        ref_number = f"SAL-{salary.created_at.strftime('%Y%m%d')}-{salary_id:03d}"

        context = {
            "employee": employee,
            "base_salary": base_salary,
            "production_bonus": production_bonus,
            "deductions": deductions,
            "final_salary": final_salary,
            "note": note,
            "created_at": salary.created_at,
            "ref_number": ref_number,
        }

        html = get_template("payroll/salary_pdf.html").render(context)
        pdf_dir = os.path.join(settings.MEDIA_ROOT, "salaries")
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"{ref_number}.pdf")
        HTML(string=html).write_pdf(target=pdf_path)

        return redirect("salary_list")

    employees = Employee.objects.all()
    return render(request, "payroll/add_salary.html", {"employees": employees})


def manage_policy_settings(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        formset = PolicySettingFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect("manage_policy_settings")
    else:
        formset = PolicySettingFormSet()
    return render(request, "payroll/policy_settings.html", {"formset": formset})


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "payroll/index.html")


def app_home(request: HttpRequest) -> HttpResponse:
    return render(request, "apps/payroll/home.html", {"app": "payroll"})
