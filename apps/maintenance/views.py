from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.utils import timezone
from weasyprint import HTML

from core.utils import export_to_excel

from .forms import MaintenanceLogForm, MaintenanceRequestForm
from .models import MaintenanceLog, MaintenanceRequest


# 🛠️ تسجيل صيانة
def log_maintenance(request):
    if request.method == "POST":
        form = MaintenanceLogForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("maintenance:maintenance_logs")
    else:
        form = MaintenanceLogForm()
    return render(request, "maintenance/log_maintenance.html", {"form": form})


# 📋 عرض سجل الصيانة مع الفلترة
def maintenance_logs(request):
    logs = MaintenanceLog.objects.select_related("machine").order_by(
        "-maintenance_date"
    )

    machine = request.GET.get("machine")
    issue = request.GET.get("issue")
    date_from = request.GET.get("from")
    date_to = request.GET.get("to")

    if machine:
        logs = logs.filter(machine__name__icontains=machine)
    if issue:
        logs = logs.filter(issue__icontains=issue)
    if date_from and date_to:
        logs = logs.filter(maintenance_date__range=[date_from, date_to])

    # 🔔 تنبيه ذكي
    today = timezone.now().date()
    alerts = []
    overdue = logs.filter(next_maintenance__lt=today)
    if overdue.exists():
        for log in overdue:
            alerts.append(
                f"⚠️ الصيانة الدورية للماكينة {log.machine.name} متأخرة (كان المفترض: {log.next_maintenance})"
            )

    # 🔁 تحليل الأعطال المتكررة
    frequent = (
        MaintenanceLog.objects.values("machine__name")
        .annotate(total=Count("id"))
        .filter(total__gt=3)
    )

    context = {
        "logs": logs,
        "filters": {
            "machine": machine,
            "issue": issue,
            "from": date_from,
            "to": date_to,
        },
        "alerts": alerts,
        "frequent_issues": frequent,
    }
    return render(request, "maintenance/maintenance_logs.html", context)


# 🖨️ تصدير PDF لسجل الصيانة
def maintenance_logs_pdf(request):
    logs = MaintenanceLog.objects.select_related("machine").order_by(
        "-maintenance_date"
    )
    html = get_template("maintenance/maintenance_logs_pdf.html").render({"logs": logs})
    pdf_file = HTML(string=html).write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'filename="maintenance_logs.pdf"'
    return response


# 📊 تصدير Excel لسجل الصيانة
def maintenance_logs_excel(request):
    logs = MaintenanceLog.objects.select_related("machine").order_by(
        "-maintenance_date"
    )
    data = []
    for log in logs:
        data.append(
            {
                "الماكينة": log.machine.name,
                "التاريخ": log.maintenance_date.strftime("%Y-%m-%d"),
                "العطل": log.issue,
                "الإجراء": log.action_taken,
                "الفني": log.technician,
                "الصيانة القادمة": (
                    log.next_maintenance.strftime("%Y-%m-%d")
                    if log.next_maintenance
                    else ""
                ),
            }
        )
    return export_to_excel(data, filename="maintenance_logs.xlsx")


# 📋 عرض طلبات الصيانة
def maintenance_requests(request):
    requests = MaintenanceRequest.objects.select_related(
        "machine", "reported_by"
    ).order_by("-request_date")

    machine = request.GET.get("machine")
    status = request.GET.get("status")

    if machine:
        requests = requests.filter(machine__name__icontains=machine)
    if status:
        requests = requests.filter(status=status)

    return render(
        request,
        "maintenance/maintenance_requests.html",
        {
            "requests": requests,
            "filters": {"machine": machine, "status": status},
        },
    )


# ➕ إنشاء طلب صيانة
def create_maintenance_request(request):
    if request.method == "POST":
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("maintenance:maintenance_requests")
    else:
        form = MaintenanceRequestForm()
    return render(request, "maintenance/create_request.html", {"form": form})


# 🖨️ تصدير PDF لطلبات الصيانة
def maintenance_requests_pdf(request):
    requests = MaintenanceRequest.objects.select_related(
        "machine", "reported_by"
    ).order_by("-request_date")
    html = get_template("maintenance/maintenance_requests_pdf.html").render(
        {"requests": requests}
    )
    pdf_file = HTML(string=html).write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'filename="maintenance_requests.pdf"'
    return response


# 📊 تصدير Excel لطلبات الصيانة
def maintenance_requests_excel(request):
    requests = MaintenanceRequest.objects.select_related(
        "machine", "reported_by"
    ).order_by("-request_date")
    data = []
    for r in requests:
        data.append(
            {
                "الماكينة": r.machine.name,
                "المبلغ": r.reported_by.name if r.reported_by else "-",
                "تاريخ الطلب": r.request_date.strftime("%Y-%m-%d"),
                "الحالة": dict(r._meta.get_field("status").choices).get(r.status),
                "الوصف": r.issue_description,
                "ملاحظات": r.resolution_notes or "",
            }
        )
    return export_to_excel(data, filename="maintenance_requests.xlsx")


def index(request):
    return render(request, "maintenance/index.html")


def app_home(request):
    return render(request, "apps/maintenance/home.html", {"app": "maintenance"})
