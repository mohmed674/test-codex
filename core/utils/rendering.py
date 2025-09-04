# core/utils/rendering.py
from typing import Any

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import CSS, HTML


def render_to_pdf_weasy(
    template_src: str,
    context: dict[str, Any] | None = None,
    filename: str = "output.pdf",
) -> HttpResponse:
    """
    توليد ملف PDF من قالب HTML باستخدام WeasyPrint.
    يقبل context كقاموس (dict) اختياري. يتم تحويل أي Mapping إلى dict لضمان توافق typing.
    """
    # ضمان أن الـ context قاموس وفق توقيع Django typings
    if context is not None and not isinstance(context, dict):
        context = dict(context)  # type: ignore[arg-type]

    html_string = render_to_string(template_src, context)
    html = HTML(string=html_string, base_url=(settings.STATIC_ROOT or None))
    pdf_bytes = html.write_pdf(
        stylesheets=[CSS(string="@page { size: A4; margin: 1cm }")]
    )

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response
