# core/utils/pdf_render.py
from __future__ import annotations

from io import BytesIO
from typing import Any, Mapping, Optional

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import CSS, HTML
from xhtml2pdf import pisa


# ✅ الطريقة الأولى – WeasyPrint (مظهر احترافي)
def render_to_pdf_weasy(
    template_path: str,
    context: Mapping[str, Any] | None = None,
    *,
    filename: str = "report.pdf",
    as_attachment: bool = False,
) -> HttpResponse:
    tpl = get_template(template_path)
    html_str = tpl.render(dict(context or {}))
    base_url = settings.STATIC_ROOT or settings.STATIC_URL or None  # type: ignore[assignment]

    pdf_bytes = HTML(string=html_str, base_url=base_url).write_pdf(
        stylesheets=[CSS(string="@page { size: A4; margin: 1cm }")]
    )

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    disposition = "attachment" if as_attachment else "inline"
    response["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return response


# ✅ الطريقة الثانية – xhtml2pdf (توافق أعلى مع HTML بسيط)
def render_to_pdf_pisa(
    template_path: str,
    context: Mapping[str, Any] | None = None,
    *,
    filename: str = "report.pdf",
    as_attachment: bool = False,
) -> Optional[HttpResponse]:
    tpl = get_template(template_path)
    html_str = tpl.render(dict(context or {}))

    buffer = BytesIO()
    pdf: Any = pisa.CreatePDF(src=html_str, dest=buffer, encoding="utf-8")

    if pdf.err:  # type: ignore[attr-defined]
        return None

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    disposition = "attachment" if as_attachment else "inline"
    response["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return response
