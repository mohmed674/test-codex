from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from weasyprint import HTML

# ✅ الطريقة الأولى – WeasyPrint (مفضلة للمظهر الاحترافي)
def render_to_pdf_weasy(template_path, context, filename="report.pdf"):
    template = get_template(template_path)
    html = template.render(context)
    pdf_file = HTML(string=html, base_url=None).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{filename}"'
    return response


# ✅ الطريقة الثانية – xhtml2pdf (أسهل توافقًا مع HTML التقليدي)
def render_to_pdf_pisa(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
