from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML
import openpyxl
import tempfile

def export_attendance_pdf(records):
    template = get_template('attendance/attendance_pdf.html')
    html = template.render({'records': records})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance.pdf"'

    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as output:
        HTML(string=html).write_pdf(output.name)
        output.seek(0)
        response.write(output.read())

    return response


def export_attendance_excel(records):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Attendance"
    ws.append(['اسم الموظف', 'التاريخ', 'الحالة'])

    for r in records:
        ws.append([r.evaluation.employee.name, r.date.strftime('%Y-%m-%d'), r.status])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=attendance.xlsx'
    wb.save(response)
    return response


def export_lateness_absence_excel(entries):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Lateness & Absence"
    ws.append(['اسم الموظف', 'التاريخ', 'الحالة'])

    for entry in entries:
        ws.append([entry.evaluation.employee.name, entry.date.strftime('%Y-%m-%d'), entry.status])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lateness_absence.xlsx'
    wb.save(response)
    return response
