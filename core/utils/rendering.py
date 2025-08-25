# core/utils/rendering.py

from weasyprint import HTML, CSS
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import os


def render_to_pdf_weasy(template_src, context_dict, filename="output.pdf"):
    """
    توليد ملف PDF من قالب HTML باستخدام WeasyPrint
    """
    html_string = render_to_string(template_src, context_dict)
    html = HTML(string=html_string, base_url=settings.STATIC_ROOT)

    pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 1cm }')])

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
