from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from apps.discipline.models import DisciplineRecord
from datetime import datetime
import openpyxl
from weasyprint import HTML

def discipline_report(request):
    name = request.GET.get('name', '').strip()
    action_type = request.GET.get('action_type', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    records = DisciplineRecord.objects.select_related('employee').all()

    if name:
        records = records.filter(employee__name__icontains=name)
    if action_type:
        records = records.filter(type=action_type)
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

    # تصدير Excel
    if request.GET.get('export') == '1':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Discipline Records"
        ws.append(['اسم الموظف', 'نوع الإجراء', 'القيمة', 'السبب', 'أنشئ بواسطة', 'التاريخ'])

        for r in records:
            ws.append([
                r.employee.name,
                r.type,
                str(r.value) if r.value else '-',
                r.reason,
                r.created_by,
                r.date.strftime('%Y-%m-%d')
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=discipline_report.xlsx'
        wb.save(response)
        return response

    # تصدير PDF باستخدام WeasyPrint
    if request.GET.get('download_pdf') == '1':
        html_string = render_to_string('discipline/discipline_report.html', {
            'records': records,
            'request': request
        })
        html = HTML(string=html_string)
        result = html.write_pdf()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename=discipline_report.pdf'
        response.write(result)
        return response

    return render(request, 'discipline/discipline_report.html', {
        'records': records
    })

def manager_discipline_report(request):
    # يمكنك تخصيص فلترة المدير إذا أردت لاحقاً، الآن يعرض كل السجلات
    name = request.GET.get('name', '').strip()
    action_type = request.GET.get('action_type', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    records = DisciplineRecord.objects.select_related('employee').all()

    if name:
        records = records.filter(employee__name__icontains=name)
    if action_type:
        records = records.filter(type=action_type)
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

    # تصدير Excel
    if request.GET.get('export') == '1':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Manager Discipline Records"
        ws.append(['اسم الموظف', 'نوع الإجراء', 'القيمة', 'السبب', 'أنشئ بواسطة', 'التاريخ'])

        for r in records:
            ws.append([
                r.employee.name,
                r.type,
                str(r.value) if r.value else '-',
                r.reason,
                r.created_by,
                r.date.strftime('%Y-%m-%d')
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=manager_discipline_report.xlsx'
        wb.save(response)
        return response

    # تصدير PDF
    if request.GET.get('download_pdf') == '1':
        html_string = render_to_string('discipline/manager_discipline_report.html', {
            'records': records,
            'request': request
        })
        html = HTML(string=html_string)
        result = html.write_pdf()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename=manager_discipline_report.pdf'
        response.write(result)
        return response

    return render(request, 'discipline/manager_discipline_report.html', {
        'records': records
    })
