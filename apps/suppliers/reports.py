# ERP_CORE/suppliers/reports.py

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Supplier

def export_supplier_list_pdf(request):
    suppliers = Supplier.objects.all()
    html_string = render_to_string('suppliers/pdf/supplier_list_pdf.html', {'suppliers': suppliers})
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="suppliers_list.pdf"'
    return response
