# export_utils.py
import os
from io import BytesIO

import pandas as pd
from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.timezone import now

# محاولات اختيارية لمحرّكات PDF
try:
    from weasyprint import HTML, CSS  # type: ignore
    _HAS_WEASYPRINT = True
except Exception:
    _HAS_WEASYPRINT = False

try:
    from xhtml2pdf import pisa  # type: ignore
    _HAS_PISA = True
except Exception:
    _HAS_PISA = False


def export_to_excel(data, columns=None, filename: str = "report.xlsx", sheet_name: str = "Sheet1") -> HttpResponse:
    """
    يدعم:
    - list[dict] أو DataFrame أو QuerySet.values()
    - columns اختياري لإعادة الترتيب/الانتقاء
    """
    # تطبيع إلى DataFrame
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    elif hasattr(data, "values") and callable(getattr(data, "values", None)):
        # QuerySet.values()
        try:
            df = pd.DataFrame(list(data.values()))
        except Exception:
            df = pd.DataFrame(list(data))
    elif isinstance(data, (list, tuple)):
        if data and not isinstance(data[0], dict) and columns:
            # قائمة كائنات + تحديد أعمدة
            rows = [{col: getattr(obj, col, "") for col in columns} for obj in data]
            df = pd.DataFrame(rows, columns=columns)
        else:
            df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(data)

    # ترتيب/استكمال الأعمدة إن طُلِبت
    if columns:
        for c in columns:
            if c not in df.columns:
                df[c] = ""
        df = df.loc[:, columns]

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    buffer.seek(0)

    resp = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


def _link_callback(uri: str, rel: str) -> str:
    """حلّ مسارات static/media لـ xhtml2pdf."""
    if uri.startswith(("http://", "https://")):
        return uri
    if settings.MEDIA_URL and uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
        return path
    if settings.STATIC_URL and uri.startswith(settings.STATIC_URL):
        found = finders.find(uri.replace(settings.STATIC_URL, ""))
        return found or uri
    return uri


def render_to_pdf(template_src: str, context_dict=None, filename: str | None = None, inline: bool = True) -> HttpResponse:
    """
    يولد PDF من قالب Django.
    - يستخدم WeasyPrint إن وُجد، وإلا يسقط إلى xhtml2pdf.
    - يضيف generated_at تلقائيًا إن غاب.
    - filename اختياري لتحديد اسم الملف و Content-Disposition.
    """
    context = dict(context_dict or {})
    context.setdefault("generated_at", now())

    template = get_template(template_src)
    html = template.render(context)

    base_url = None
    req = context.get("request")
    if req:
        try:
            base_url = req.build_absolute_uri("/")
        except Exception:
            base_url = None

    if _HAS_WEASYPRINT:
        try:
            css = CSS(string="@page { size: A4; margin: 18mm 12mm; }")
            pdf_bytes = HTML(string=html, base_url=base_url).write_pdf(stylesheets=[css])
            resp = HttpResponse(pdf_bytes, content_type="application/pdf")
            disp = "inline" if inline else "attachment"
            if filename:
                resp["Content-Disposition"] = f'{disp}; filename="{filename}"'
            return resp
        except Exception:
            pass  # سيجري fallback

    if _HAS_PISA:
        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=buffer, link_callback=_link_callback)
        if pisa_status.err:
            return HttpResponse("PDF generation error", status=500)
        buffer.seek(0)
        resp = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        disp = "inline" if inline else "attachment"
        if filename:
            resp["Content-Disposition"] = f'{disp}; filename="{filename}"'
        return resp

    # كحل أخير: إرجاع HTML خام
    return HttpResponse(html, content_type="text/html; charset=utf-8")
