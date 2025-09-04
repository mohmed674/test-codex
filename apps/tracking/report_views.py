# ERP_CORE/tracking/report_views.py

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from weasyprint import HTML

from core.utils import export_to_excel

from .models import ProductTracking


# 📄 العرض العادي للتقرير
def tracking_report(request):
    records = ProductTracking.objects.all().order_by("-shipment_date")

    # فلترة ذكية
    product_name = request.GET.get("product_name")
    tracking_code = request.GET.get("tracking_code")
    payment_method = request.GET.get("payment_method")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if product_name:
        records = records.filter(product_name__icontains=product_name)
    if tracking_code:
        records = records.filter(tracking_code__icontains=tracking_code)
    if payment_method:
        records = records.filter(payment_method__icontains=payment_method)
    if date_from and date_to:
        records = records.filter(shipment_date__range=[date_from, date_to])

    context = {
        "records": records,
        "filters": {
            "product_name": product_name,
            "tracking_code": tracking_code,
            "payment_method": payment_method,
            "date_from": date_from,
            "date_to": date_to,
        },
    }
    return render(request, "tracking/tracking_pdf.html", context)


# 🖨️ PDF تصدير
def tracking_report_pdf(request):
    response = tracking_report(request)
    html = get_template("tracking/tracking_pdf.html").render(response.context_data)
    pdf = HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="tracking_report.pdf"'
    return response


# 📊 Excel تصدير
def tracking_report_excel(request):
    records = ProductTracking.objects.all().order_by("-shipment_date")

    product_name = request.GET.get("product_name")
    tracking_code = request.GET.get("tracking_code")
    payment_method = request.GET.get("payment_method")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if product_name:
        records = records.filter(product_name__icontains=product_name)
    if tracking_code:
        records = records.filter(tracking_code__icontains=tracking_code)
    if payment_method:
        records = records.filter(payment_method__icontains=payment_method)
    if date_from and date_to:
        records = records.filter(shipment_date__range=[date_from, date_to])

    export_data = []
    for r in records:
        export_data.append(
            {
                "اسم المنتج": r.product_name,
                "كود التتبع": r.tracking_code,
                "اسم العميل": r.customer_name,
                "طريقة الدفع": r.get_payment_method_display(),
                "الحالة": r.get_status_display(),
                "تاريخ الشحن": r.shipment_date.strftime("%Y-%m-%d"),
                "تاريخ التسليم": (
                    r.delivery_date.strftime("%Y-%m-%d") if r.delivery_date else ""
                ),
            }
        )

    return export_to_excel(export_data, filename="tracking_report.xlsx")
