# core/utils/export_excel.py
from __future__ import annotations

import io
from typing import Any, Iterable, Mapping

import pandas as pd
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML


def _normalize_rows(
    data: Any,
) -> list[dict[str, Any]]:
    """
    يحول أي مصدر بيانات إلى قائمة من القواميس:
    - QuerySet.values() → list[dict]
    - list[dict]        → كما هي
    - list[objects]     → يحاول تحويلها عبر __dict__ البسيط
    """
    if hasattr(data, "values"):  # مثل QuerySet
        return list(data.values())
    if isinstance(data, list):
        if data and isinstance(data[0], Mapping):
            return list(data)  # list[dict]
        # fallback: list of objects
        out: list[dict[str, Any]] = []
        for x in data:
            if isinstance(x, Mapping):
                out.append(dict(x))
            else:
                # محاولة آمنة لاستخراج الحقول الشائعة
                out.append(
                    {
                        k: v
                        for k, v in getattr(x, "__dict__", {}).items()
                        if not k.startswith("_")
                    }
                )
        return out
    if isinstance(data, Iterable):
        # Iterable من dicts
        return [
            dict(row) if isinstance(row, Mapping) else {"value": row} for row in data
        ]
    return []


# ✅ تصدير قائمة عامة إلى Excel
def export_to_excel(
    data: Any,
    filename: str = "export.xlsx",
    field_verbose_names: Mapping[str, str] | None = None,
) -> HttpResponse:
    rows = _normalize_rows(data)
    df = pd.DataFrame(rows)
    if field_verbose_names:
        df.rename(columns=dict(field_verbose_names), inplace=True)

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# ✅ تصدير قائمة عامة إلى CSV
def export_to_csv(
    data: Any,
    filename: str = "export.csv",
    field_verbose_names: Mapping[str, str] | None = None,
) -> HttpResponse:
    rows = _normalize_rows(data)
    df = pd.DataFrame(rows)
    if field_verbose_names:
        df.rename(columns=dict(field_verbose_names), inplace=True)

    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")
    csv_text = buffer.getvalue()

    response = HttpResponse(csv_text, content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# ✅ تصدير فاتورة محددة إلى Excel (باستخدام invoice.items)
def export_invoice_to_excel(
    invoice: Any, filename: str = "invoice.xlsx"
) -> HttpResponse:
    data = [
        {
            "المنتج": getattr(item.product, "name", ""),
            "الكمية": getattr(item, "quantity", ""),
            "السعر": getattr(item, "price", ""),
            "الإجمالي": getattr(item, "total", ""),
        }
        for item in invoice.items.all()
    ]

    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# ✅ تصدير فاتورة إلى PDF
def render_invoice_pdf(
    template_name: str,
    context: Mapping[str, Any] | None = None,
    filename: str = "invoice.pdf",
) -> HttpResponse:
    template = get_template(template_name)
    html = template.render(dict(context or {}))
    pdf_file = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'filename="{filename}"'
    return response
