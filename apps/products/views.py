from __future__ import annotations

import csv
import importlib
from contextlib import suppress
from io import BytesIO
from typing import Any, Callable, Dict, Optional, Tuple, cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_http_methods

from .forms import FinishedProductForm
from .models import FinishedProduct

# ====== تصدير/طباعة: حلّ مرن لمسارات متعددة + إزالة تحذيرات mypy (no-redef) ======
ExportCallable = Callable[..., HttpResponse]

def _load_export_utils() -> Tuple[Optional[ExportCallable], Optional[ExportCallable]]:
  """يحاول جلب export_to_excel / render_to_pdf من عدة مسارات بدون إعادة تعريفات."""
  candidates = (
      "export_utils",
      "core.export_utils",
      "common.export_utils",
  )
  export_to_excel: Optional[ExportCallable] = None
  render_to_pdf: Optional[ExportCallable] = None

  for mod_path in candidates:
      with suppress(Exception):
          mod = importlib.import_module(mod_path)  # type: ignore[import]
          # getattr داخل suppress لتفادي AttributeError
          with suppress(Exception):
              export_to_excel = cast(ExportCallable, getattr(mod, "export_to_excel"))
          with suppress(Exception):
              render_to_pdf = cast(ExportCallable, getattr(mod, "render_to_pdf"))
          if export_to_excel and render_to_pdf:
              break
  return export_to_excel, render_to_pdf

_ext_export_to_excel, _ext_render_to_pdf = _load_export_utils()

if not _ext_export_to_excel or not _ext_render_to_pdf:
    # Fallbacks محلية إذا لم تتوفر util خارجي
    import pandas as pd
    from django.template.loader import get_template
    from django.utils.timezone import now

    def _fallback_export_to_excel(
        data: Any,
        columns: Optional[list[str]] = None,
        filename: str = "report.xlsx",
        sheet_name: str = "Sheet1",
    ) -> HttpResponse:
        # تطبيع البيانات إلى DataFrame
        if isinstance(data, pd.DataFrame):
            df = data.copy()
        elif hasattr(data, "values") and callable(getattr(data, "values", None)):
            # QuerySet.values()
            with suppress(Exception):
                df = pd.DataFrame(list(data.values()))
            if "df" not in locals():
                df = pd.DataFrame(list(data))  # type: ignore[arg-type]
        elif isinstance(data, (list, tuple)):
            df = pd.DataFrame(data)
        else:
            with suppress(Exception):
                df = pd.DataFrame(list(data))  # type: ignore[arg-type]
            if "df" not in locals():
                df = pd.DataFrame()

        # ترتيب/استكمال الأعمدة
        if columns:
            for c in columns:
                if c not in df.columns:
                    df[c] = ""
            df = df.loc[:, columns]

        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
        buf.seek(0)

        resp = HttpResponse(
            buf.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp

    def _fallback_render_to_pdf(
        template_src: str,
        context_dict: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
        inline: bool = True,
    ) -> HttpResponse:
        context = dict(context_dict or {})
        context.setdefault("generated_at", now())
        html = get_template(template_src).render(context)

        # WeasyPrint أولاً
        with suppress(Exception):
            from weasyprint import CSS, HTML  # type: ignore

            pdf_bytes = HTML(string=html).write_pdf(
                stylesheets=[CSS(string="@page { size: A4; margin: 18mm 12mm; }")]
            )
            resp = HttpResponse(pdf_bytes, content_type="application/pdf")
            disp = "inline" if inline else "attachment"
            if filename:
                resp["Content-Disposition"] = f'{disp}; filename="{filename}"'
            return resp

        # xhtml2pdf ثانيًا
        with suppress(Exception):
            from xhtml2pdf import pisa  # type: ignore

            buf = BytesIO()
            status = pisa.CreatePDF(html, dest=buf)
            if getattr(status, "err", 1):
                return HttpResponse("PDF generation error", status=500)
            buf.seek(0)
            resp = HttpResponse(buf.getvalue(), content_type="application/pdf")
            disp = "inline" if inline else "attachment"
            if filename:
                resp["Content-Disposition"] = f'{disp}; filename="{filename}"'
            return resp

        # أخيرًا HTML خام
        return HttpResponse(html, content_type="text/html; charset=utf-8")

    export_to_excel: ExportCallable = _fallback_export_to_excel
    render_to_pdf: ExportCallable = _fallback_render_to_pdf
else:
    export_to_excel = _ext_export_to_excel
    render_to_pdf = _ext_render_to_pdf

# ===== مساعدات محلية =====
ALLOWED_ORDERING = {
    "product_code",
    "name",
    "quantity",
    "date_produced",
    "expiration_date",
    "expiry_date",  # دعم قديم
    "quality_status",
    "created_at",
    "updated_at",
}

def t(msg: str) -> str:
    """ترجمة كسلسلة نصية صريحة (لتجنّب _StrPromise في typing)."""
    return str(_(msg))

def _fmt_date(d: Any) -> str:
    if not d:
        return "-"
    with suppress(Exception):
        return d.strftime("%Y-%m-%d")
    with suppress(Exception):
        return timezone.localtime(d).date().strftime("%Y-%m-%d")
    return str(d)

def _coalesce_attr(obj: Any, *names: str, default: Any = None) -> Any:
    for n in names:
        with suppress(Exception):
            val = getattr(obj, n)
            if val is not None:
                return val
    return default

def _safe_days_to_expiry(expiry: Any) -> Optional[int]:
    with suppress(Exception):
        if not expiry:
            return None
        today = timezone.localdate()
        with suppress(Exception):
            exp_date = (
                expiry
                if hasattr(expiry, "year") and not hasattr(expiry, "hour")
                else timezone.localtime(expiry).date()
            )
            return (exp_date - today).days
        exp_date = getattr(expiry, "date", lambda: None)() or expiry
        return (exp_date - today).days
    return None

def _model_has_field(model: Any, field_name: str) -> bool:
    with suppress(Exception):
        return any(f.name == field_name for f in model._meta.get_fields())  # type: ignore[attr-defined]
    return False

def _try_filter(qs, **kwargs):
    try:
        return qs.filter(**kwargs)
    except FieldError:
        return qs
    except Exception:
        return qs

# 📦 قائمة المنتجات (فلترة/ترتيب/تصدير/طباعة/JSON)
@require_GET
@login_required
def product_list(request: HttpRequest) -> HttpResponse:
    qs = FinishedProduct.objects.all().select_related()

    # فلاتر
    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()
    qstatus = (request.GET.get("quality_status") or "").strip()
    date_from = (request.GET.get("date_from") or "").strip()
    date_to = (request.GET.get("date_to") or "").strip()
    ordering = (request.GET.get("ordering") or "").strip()
    fmt = (request.GET.get("format") or "").lower()

    if q:
        qs = qs.filter(Q(product_code__icontains=q) | Q(name__icontains=q))

    # توحيد فلتر الحالة
    effective_status = qstatus or status
    if effective_status:
        if _model_has_field(FinishedProduct, "quality_status"):
            qs = _try_filter(qs, quality_status=effective_status)
        else:
            qs = _try_filter(qs, status=effective_status)

    # نطاق التاريخ على date_produced مع تحمّل نوع الحقل (Date/DateTime)
    def _apply_date_filter(queryset, field, gte=None, lte=None):
        qset = queryset
        if gte:
            with suppress(Exception):
                return qset.filter(**{f"{field}__date__gte": gte})
            qset = qset.filter(**{f"{field}__gte": gte})
        if lte:
            with suppress(Exception):
                return qset.filter(**{f"{field}__date__lte": lte})
            qset = qset.filter(**{f"{field}__lte": lte})
        return qset

    with suppress(Exception):
        if date_from:
            qs = _apply_date_filter(qs, "date_produced", gte=date_from)
        if date_to:
            qs = _apply_date_filter(qs, "date_produced", lte=date_to)

    # ترتيب آمن
    if ordering:
        base = ordering.lstrip("-")
        if base in ALLOWED_ORDERING:
            with suppress(Exception):
                qs = qs.order_by(ordering)
            if base == "expiry_date":
                qs = qs.order_by(ordering.replace("expiry_date", "expiration_date"))

    # تصدير/طباعة قبل التقسيم لصفحات
    if "download_pdf" in request.GET:
        return render_to_pdf(
            "products/products_pdf.html",
            {"products": qs, "request": request},
            filename="finished_products.pdf",
            inline=True,
        )

    export = (request.GET.get("export") or "").lower()
    if export in {"excel", "xlsx", "csv", "json"} or fmt == "json":
        rows: list[Dict[str, Any]] = []
        for p in qs:
            expiry = _coalesce_attr(p, "expiration_date", "expiry_date")

            # عرض الحالة المتوافقة بدون أخطاء typing
            status_disp = "-"
            method = getattr(p, "get_quality_status_display", None)
            if callable(method):
                with suppress(Exception):
                    status_disp = method()
            else:
                method2 = getattr(p, "get_status_display", None)
                if callable(method2):
                    with suppress(Exception):
                        status_disp = method2()

            rows.append(
                {
                    t("كود المنتج"): getattr(p, "product_code", ""),
                    t("الاسم"): getattr(p, "name", ""),
                    t("الكمية"): getattr(p, "quantity", 0),
                    t("الحالة"): status_disp,
                    t("تاريخ الإنتاج"): _fmt_date(getattr(p, "date_produced", None)),
                    t("تاريخ الانتهاء"): _fmt_date(expiry),
                    t("الأيام حتى الانتهاء"): _safe_days_to_expiry(expiry),
                }
            )

        if export in {"excel", "xlsx"}:
            columns: list[str] = [
                t("كود المنتج"),
                t("الاسم"),
                t("الكمية"),
                t("الحالة"),
                t("تاريخ الإنتاج"),
                t("تاريخ الانتهاء"),
                t("الأيام حتى الانتهاء"),
            ]
            return export_to_excel(
                rows, columns=columns, filename="finished_products.xlsx"
            )
        if export == "json" or fmt == "json":
            return JsonResponse(
                rows, safe=False, json_dumps_params={"ensure_ascii": False}
            )
        if export == "csv":
            resp = HttpResponse(content_type="text/csv; charset=utf-8")
            resp["Content-Disposition"] = 'attachment; filename="finished_products.csv"'
            w = csv.writer(resp)
            if rows:
                w.writerow(rows[0].keys())
                for r in rows:
                    w.writerow(r.values())
            else:
                w.writerow([t("لا توجد بيانات")])
            return resp

    # تقسيم صفحات
    page = request.GET.get("page", 1)
    paginator = Paginator(qs, 25)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    ctx = {
        "products": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "filters": {
            "q": q,
            "status": effective_status,
            "date_from": date_from,
            "date_to": date_to,
            "ordering": ordering,
        },
    }
    return render(request, "products/product_list.html", ctx)

# ➕ إنشاء منتج نهائي
@require_http_methods(["GET", "POST"])
@login_required
def product_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = FinishedProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            with suppress(Exception):
                messages.success(request, _("تم إنشاء المنتج بنجاح."))
            return redirect("products:product_list")
    else:
        form = FinishedProductForm()
    return render(request, "products/product_form.html", {"form": form})

# ✏️ تعديل منتج
@require_http_methods(["GET", "POST"])
@login_required
def product_edit(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(FinishedProduct, pk=pk)
    if request.method == "POST":
        form = FinishedProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            with suppress(Exception):
                messages.success(request, _("تم تعديل المنتج بنجاح."))
            return redirect("products:product_list")
    else:
        form = FinishedProductForm(instance=product)
    return render(
        request, "products/product_form.html", {"form": form, "edit_mode": True}
    )

# ❌ حذف منتج
@require_http_methods(["GET", "POST"])
@login_required
def product_delete(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(FinishedProduct, pk=pk)
    if request.method == "POST":
        product.delete()
        with suppress(Exception):
            messages.success(request, _("تم حذف المنتج بنجاح."))
        return redirect("products:product_list")
    return render(request, "products/product_confirm_delete.html", {"product": product})

def index(request: HttpRequest) -> HttpResponse:
    return render(request, "products/index.html")

def app_home(request: HttpRequest) -> HttpResponse:
    return render(request, "apps/products/home.html", {"app": "products"})
