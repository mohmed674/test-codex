import io
import pandas as pd
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML

# ✅ تصدير قائمة عامة إلى Excel
def export_to_excel(data, filename='export.xlsx', field_verbose_names=None):
    if hasattr(data, 'values'):
        data = list(data.values())

    df = pd.DataFrame(data)
    if field_verbose_names:
        df.rename(columns=field_verbose_names, inplace=True)

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ✅ تصدير قائمة عامة إلى CSV
def export_to_csv(data, filename='export.csv', field_verbose_names=None):
    if hasattr(data, 'values'):
        data = list(data.values())

    df = pd.DataFrame(data)
    if field_verbose_names:
        df.rename(columns=field_verbose_names, inplace=True)

    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ✅ تصدير فاتورة محددة إلى Excel (باستخدام invoice.items)
def export_invoice_to_excel(invoice, filename='invoice.xlsx'):
    data = [{
        "المنتج": item.product.name,
        "الكمية": item.quantity,
        "السعر": item.price,
        "الإجمالي": item.total,
    } for item in invoice.items.all()]

    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    return HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ✅ تصدير فاتورة إلى PDF
def render_invoice_pdf(template_name, context, filename="invoice.pdf"):
    template = get_template(template_name)
    html = template.render(context)
    pdf_file = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{filename}"'
    return response
