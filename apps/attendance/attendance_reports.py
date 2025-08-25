from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils.timezone import datetime
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import get_template

from core.utils import export_to_excel
from apps.employees.models import Employee
from .models import Attendance


def attendance_report(request):
    employees = Employee.objects.all()
    records = Attendance.objects.select_related('employee', 'employee__department')

    # 🔍 فلترة حسب الطلب
    employee_id = request.GET.get('employee')
    department_id = request.GET.get('department')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if employee_id:
        records = records.filter(employee_id=employee_id)
    if department_id:
        records = records.filter(employee__department_id=department_id)
    if date_from and date_to:
        records = records.filter(date__range=[date_from, date_to])

    # 📊 حساب إحصائيات
    stats = {
        "total": records.count(),
        "present": records.filter(status='present').count(),
        "absent": records.filter(status='absent').count(),
        "late": records.filter(status='late').count(),
    }

    context = {
        'records': records.order_by('-date'),
        'employees': employees,
        'stats': stats,
        'filters': {
            'employee': employee_id,
            'department': department_id,
            'from': date_from,
            'to': date_to,
        }
    }
    return render(request, 'attendance/attendance_report.html', context)


# ✅ PDF Export
def attendance_report_pdf(request):
    employees = Employee.objects.all()
    records = Attendance.objects.select_related('employee', 'employee__department')

    employee_id = request.GET.get('employee')
    department_id = request.GET.get('department')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if employee_id:
        records = records.filter(employee_id=employee_id)
    if department_id:
        records = records.filter(employee__department_id=department_id)
    if date_from and date_to:
        records = records.filter(date__range=[date_from, date_to])

    template = get_template('attendance/attendance_report_pdf.html')
    html = template.render({'records': records})
    pdf_file = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="attendance_report.pdf"'
    return response


# ✅ Excel Export
def attendance_report_excel(request):
    records = Attendance.objects.select_related('employee', 'employee__department')

    employee_id = request.GET.get('employee')
    department_id = request.GET.get('department')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if employee_id:
        records = records.filter(employee_id=employee_id)
    if department_id:
        records = records.filter(employee__department_id=department_id)
    if date_from and date_to:
        records = records.filter(date__range=[date_from, date_to])

    data = []
    for r in records:
        data.append({
            'الموظف': r.employee.name,
            'القسم': r.employee.department.name,
            'التاريخ': r.date.strftime('%Y-%m-%d'),
            'الحالة': r.get_status_display(),
            'الوقت': r.time.strftime('%H:%M') if r.time else '',
        })

    return export_to_excel(data, filename='attendance_report.xlsx')
