# ERP_CORE/purchases/views_export.py

from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML
from core.utils import export_to_excel
from .models import PurchaseRequest


def purchase_report_pdf(request):
    requests = PurchaseRequest.objects.select_related('department', 'requested_by').all()
    html = get_template('purchases/report_pdf.html').render({'requests': requests})
    pdf = HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="purchase_report.pdf"'
    return response


def purchase_report_excel(request):
    requests = PurchaseRequest.objects.select_related('department', 'requested_by').all()
    data = []
    for r in requests:
        data.append({
            'رقم الطلب': r.id,
            'القسم': r.department.name,
            'الموظف': r.requested_by.name,
            'الحالة': r.get_status_display(),
            'تاريخ الطلب': r.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    return export_to_excel(data, filename="purchase_report.xlsx")
