import datetime
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML
from .models import Salary, Advance, PaymentRecord


def salary_report(request):
    salaries = Salary.objects.all().select_related('employee')
    filter_date = request.GET.get('filter_date')
    if filter_date:
        salaries = salaries.filter(created_at__date=filter_date)

    if 'export' in request.GET:
        df = pd.DataFrame([{
            'الموظف': s.employee.name,
            'الشهر/السنة': f"{s.month}/{s.year}",
            'الراتب الأساسي': s.base_salary,
            'الحوافز': s.production_bonus,
            'الخصومات': s.deductions,
            'الصافي': s.final_salary
        } for s in salaries])
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="salaries.xlsx"'
        df.to_excel(response, index=False)
        return response

    if 'download_pdf' in request.GET:
        template = get_template("payroll/reports/salary_pdf_report.html")
        html = template.render({
            "salaries": salaries,
            "filter_date": filter_date,
            "generated_at": datetime.datetime.now()
        })
        pdf = HTML(string=html).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="salaries.pdf"'
        return response

    return render(request, "payroll/reports/salary_report.html", {
        "salaries": salaries,
        "filter_date": filter_date
    })


def advance_report(request):
    advances = Advance.objects.all().select_related('employee')

    name = request.GET.get('name')
    type_filter = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if name:
        advances = advances.filter(employee__name__icontains=name)
    if type_filter:
        advances = advances.filter(type=type_filter)
    if date_from:
        advances = advances.filter(date__gte=date_from)
    if date_to:
        advances = advances.filter(date__lte=date_to)

    if 'export' in request.GET:
        df = pd.DataFrame([{
            'الموظف': a.employee.name,
            'النوع': 'أسبوعية' if a.type == 'weekly' else 'شهرية',
            'المبلغ': a.amount,
            'التاريخ': a.date.strftime("%Y-%m-%d"),
            'ملاحظة': a.note or ''
        } for a in advances])
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="advances.xlsx"'
        df.to_excel(response, index=False)
        return response

    if 'download_pdf' in request.GET:
        template = get_template("payroll/reports/advance_pdf_report.html")
        html = template.render({
            "advances": advances,
            "name": name,
            "type": type_filter,
            "date_from": date_from,
            "date_to": date_to,
            "generated_at": datetime.datetime.now()
        })
        pdf = HTML(string=html).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="advances.pdf"'
        return response

    return render(request, "payroll/reports/advance_report.html", {
        "advances": advances,
        "name": name,
        "type": type_filter,
        "date_from": date_from,
        "date_to": date_to
    })


def payment_report(request):
    payments = PaymentRecord.objects.all().select_related("employee")

    name = request.GET.get("name")
    type_filter = request.GET.get("type")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if name:
        payments = payments.filter(employee__name__icontains=name)
    if type_filter:
        payments = payments.filter(type=type_filter)
    if date_from:
        payments = payments.filter(date__gte=date_from)
    if date_to:
        payments = payments.filter(date__lte=date_to)

    if "export" in request.GET:
        df = pd.DataFrame([{
            "اسم الموظف": p.employee.name,
            "المبلغ": p.amount,
            "النوع": "أسبوعي" if p.type == "weekly" else "شهري",
            "التاريخ": p.date.strftime("%Y-%m-%d"),
            "ملاحظة": p.note or ""
        } for p in payments])
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="payments.xlsx"'
        df.to_excel(response, index=False)
        return response

    if "download_pdf" in request.GET:
        template = get_template("payroll/reports/payment_pdf_report.html")
        html = template.render({
            "payments": payments,
            "name": name,
            "type": type_filter,
            "date_from": date_from,
            "date_to": date_to,
            "generated_at": datetime.datetime.now()
        })
        pdf = HTML(string=html).write_pdf()
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'filename="payments.pdf"'
        return response

    return render(request, "payroll/reports/payment_report.html", {
        "payments": payments,
        "name": name,
        "type": type_filter,
        "date_from": date_from,
        "date_to": date_to
    })
