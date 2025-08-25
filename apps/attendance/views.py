from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Attendance
from .forms import AttendanceForm
from apps.evaluation.models import LatenessAbsence
from django.template.loader import get_template
from datetime import datetime
from apps.attendance.exports.attendance_exports import (
    export_attendance_pdf,
    export_attendance_excel,
    export_lateness_absence_excel
)


# ✅ تسجيل حضور جديد
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('attendance_list')
    else:
        form = AttendanceForm()

    return render(request, 'attendance/input.html', {'form': form})


# ✅ قائمة الحضور + تصدير
def attendance_list(request):
    name = request.GET.get('name', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    status = request.GET.get('status', '').strip()

    records = Attendance.objects.select_related('evaluation__employee').all()

    if name:
        records = records.filter(evaluation__employee__name__icontains=name)

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            records = records.filter(date__gte=date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
            records = records.filter(date__lte=date_to_obj)
        except ValueError:
            pass

    if status:
        records = records.filter(status=status)

    # ✅ تصدير Excel
    if request.GET.get('export') == 'excel':
        return export_attendance_excel(records)

    # ✅ تصدير PDF
    if request.GET.get('export') == 'pdf':
        return export_attendance_pdf(records)

    return render(request, 'attendance/attendance_list.html', {
        'records': records
    })


# ✅ عرض وطباعة تقرير التأخير والغياب
def lateness_absence_list(request):
    name = request.GET.get('name', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    status = request.GET.get('status', '').strip()

    entries = LatenessAbsence.objects.select_related('evaluation__employee').all()

    if name:
        entries = entries.filter(evaluation__employee__name__icontains=name)

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            entries = entries.filter(date__gte=date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
            entries = entries.filter(date__lte=date_to_obj)
        except ValueError:
            pass

    if status:
        entries = entries.filter(status=status)

    # ✅ تصدير Excel
    if request.GET.get('export') == 'excel':
        return export_lateness_absence_excel(entries)

    # ✅ تصدير PDF
    if request.GET.get('export') == 'pdf':
        return export_attendance_pdf(
            entries,
            template_path='attendance/lateness_absence_pdf.html',
            filename='lateness_absence.pdf'
        )

    # ✅ طباعة مباشرة
    if request.GET.get('export') == 'print':
        return render(request, 'attendance/lateness_absence_print.html', {'entries': entries})

    return render(request, 'attendance/lateness_absence_list.html', {
        'entries': entries
    })


# ✅ طباعة مباشرة لتقرير الحضور
def attendance_print_view(request):
    name = request.GET.get('name', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    status = request.GET.get('status', '').strip()

    records = Attendance.objects.select_related('evaluation__employee').all()

    if name:
        records = records.filter(evaluation__employee__name__icontains=name)

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            records = records.filter(date__gte=date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
            records = records.filter(date__lte=date_to_obj)
        except ValueError:
            pass

    if status:
        records = records.filter(status=status)

    return render(request, 'attendance/attendance_print.html', {
        'records': records
    })


from django.shortcuts import render

def index(request):
    return render(request, 'attendance/index.html')


def app_home(request):
    return render(request, 'apps/attendance/home.html', {'app': 'attendance'})
