from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from apps.discipline.models import DisciplineRecord
from apps.employees.models import Employee
from datetime import datetime
import openpyxl
from weasyprint import HTML

def discipline_list(request):
    """
    عرض قائمة بكل عقوبات الموظفين مع إمكانية التصفية.
    """
    records = DisciplineRecord.objects.all().select_related('employee').order_by('-date')

    employee_id = request.GET.get('employee_id')
    if employee_id:
        records = records.filter(employee__id=employee_id)

    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    if date_from:
        try:
            records = records.filter(date__gte=date_from)
        except Exception:
            pass
    if date_to:
        try:
            records = records.filter(date__lte=date_to)
        except Exception:
            pass

    return render(request, 'discipline/discipline_list.html', {
        'records': records,
        'employee_id': employee_id,
        'date_from': date_from,
        'date_to': date_to,
    })


def employee_discipline_history(request, employee_id):
    """
    عرض سجل عقوبات موظف معيّن مع التصدير إلى PDF وExcel.
    """
    employee = get_object_or_404(Employee, id=employee_id)

    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    records = DisciplineRecord.objects.filter(employee=employee)

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            records = records.filter(date__gte=date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            records = records.filter(date__lte=date_to_obj)
        except ValueError:
            pass

    # ✅ تصدير Excel
    if request.GET.get('export') == '1':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Employee Discipline"
        ws.append(['نوع الإجراء', 'القيمة', 'السبب', 'أنشئ بواسطة', 'التاريخ'])

        for r in records:
            ws.append([
                r.type,
                str(r.value) if r.value else '-',
                r.reason,
                str(r.created_by) if r.created_by else '-',
                r.date.strftime('%Y-%m-%d')
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=discipline_{employee.id}.xlsx'
        wb.save(response)
        return response

    # ✅ تصدير PDF
    if request.GET.get('download_pdf') == '1':
        html_string = render_to_string('discipline/employee_discipline_history.html', {
            'employee': employee,
            'records': records,
            'request': request
        })
        html = HTML(string=html_string)
        pdf_file = html.write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="discipline_{employee.id}.pdf"'
        return response

    return render(request, 'discipline/employee_discipline_history.html', {
        'employee': employee,
        'records': records
    })


from django.shortcuts import render

def index(request):
    return render(request, 'discipline/index.html')


def app_home(request):
    return render(request, 'apps/discipline/home.html', {'app': 'discipline'})
