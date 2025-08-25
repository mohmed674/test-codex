# D:\ERP_CORE\attendance\reports\attendance_reports.py

from django.http import HttpResponse

def attendance_report(request):
    return HttpResponse("Attendance Report")

def attendance_report_pdf(request):
    return HttpResponse("Attendance Report PDF")

def attendance_report_excel(request):
    return HttpResponse("Attendance Report Excel")
