# ERP_CORE/products/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.exceptions import FieldError
import csv

from .models import FinishedProduct
from .forms import FinishedProductForm

# ===== استيراد أدوات التصدير/الطباعة (تصحيح المسارات + إسكات التحذيرات) =====
try:
    from export_utils import export_to_excel, render_to_pdf  # type: ignore[import]
except Exception:
    try:
        from core.export_utils import export_to_excel, render_to_pdf  # type: ignore[import]
    except Exception:
        try:
            from common.export_utils import export_to_excel, render_to_pdf  # type: ignore[import]
        except Exception:
            # بديل محلي نهائي
            from io import BytesIO
            from django.template.loader import get_template
            from django.utils.timezone import now
            import pandas as pd

            def export_to_excel(data, columns=None, filename="report.xlsx", sheet_name="Sheet1") -> HttpResponse:
                # تطبيع البيانات
                if isinstance(data, pd.DataFrame):
                    df = data.copy()
                elif hasattr(data, "values") and callable(getattr(data, "values", None)):
                    try:
                        df = pd.DataFrame(list(data.values()))
                    except Exception:
                        df = pd.DataFrame(list(data))
                elif isinstance(data, (list, tuple)):
                    df = pd.DataFrame(data)
                else:
                    try:
                        df = pd.DataFrame(list(data))
                    except Exception:
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

            def render_to_pdf(template_src, context_dict=None, filename=None, inline=True) -> HttpResponse:
                context = dict(context_dict or {})
                context.setdefault("generated_at", now())
                html = get_template(template_src).render(context)

                # WeasyPrint أولاً
                try:
                    from weasyprint import HTML, CSS  # type: ignore
                    pdf_bytes = HTML(string=html).write_pdf(
                        stylesheets=[CSS(string="@page { size: A4; margin: 18mm 12mm; }")]
                    )
                    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
                    disp = "inline" if inline else "attachment"
                    if filename:
                        resp["Content-Disposition"] = f'{disp}; filename="{filename}"'
                    return resp
                except Exception:
                    pass

                # xhtml2pdf ثانيًا
                try:
                    from xhtml2pdf import pisa  # type: ignore
                    buf = BytesIO()
                    status = pisa.CreatePDF(html, dest=buf)
                    if status.err:
                        return HttpResponse("PDF generation error", status=500)
                    buf.seek(0)
                    resp = HttpResponse(buf.getvalue(), content_type="application/pdf")
                    disp = "inline" if inline else "attachment"
                    if filename:
                        resp["Content-Disposition"] = f'{disp}; filename="{filename}"'
                    return resp
                except Exception:
                    # أخيرًا HTML خام
                    return HttpResponse(html, content_type="text/html; charset=utf-8")


# ===== مساعدات محلية =====
# توحيد أسماء الحقول بين "expiration_date" و"expiry_date" وبين "quality_status" و"status"
ALLOWED_ORDERING = {
    "product_code",
    "name",
    "quantity",
    "date_produced",
    "expiration_date",
    "expiry_date",       # دعم قديم
    "quality_status",
    "created_at",
    "updated_at",
}

def _fmt_date(d):
    if not d:
        return "-"
    # دعم Date أو DateTime
    try:
        return d.strftime("%Y-%m-%d")
    except Exception:
        try:
            return timezone.localtime(d).date().strftime("%Y-%m-%d")
        except Exception:
            return str(d)

def _coalesce_attr(obj, *names, default=None):
    for n in names:
        try:
            val = getattr(obj, n)
            # نعتبر None كعدم توفر ونستمر
            if val is not None:
                return val
        except Exception:
            continue
    return default

def _safe_days_to_expiry(expiry):
    try:
        if not expiry:
            return None
        today = timezone.localdate()
        # دعم Date أو DateTime
        try:
            exp_date = expiry if hasattr(expiry, "year") and not hasattr(expiry, "hour") else timezone.localtime(expiry).date()
        except Exception:
            exp_date = getattr(expiry, "date", lambda: None)() or expiry
        return (exp_date - today).days
    except Exception:
        return None

def _model_has_field(model, field_name: str) -> bool:
    try:
        return any(f.name == field_name for f in model._meta.get_fields())
    except Exception:
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
def product_list(request):
    # تحسين الأداء: اختيار علاقات محتملة
    qs = FinishedProduct.objects.all().select_related()

    # فلاتر
    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()  # متوافق مع الواجهات القديمة
    qstatus = (request.GET.get("quality_status") or "").strip()  # الاسم الصحيح في الموديل
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
            try:
                qset = qset.filter(**{f"{field}__date__gte": gte})
            except Exception:
                qset = qset.filter(**{f"{field}__gte": gte})
        if lte:
            try:
                qset = qset.filter(**{f"{field}__date__lte": lte})
            except Exception:
                qset = qset.filter(**{f"{field}__lte": lte})
        return qset

    try:
        if date_from:
            qs = _apply_date_filter(qs, "date_produced", gte=date_from)
        if date_to:
            qs = _apply_date_filter(qs, "date_produced", lte=date_to)
    except Exception:
        pass

    # ترتيب آمن
    if ordering:
        base = ordering.lstrip("-")
        if base in ALLOWED_ORDERING:
            try:
                qs = qs.order_by(ordering)
            except Exception:
                # fallback: لو طُلب expiry_date نرتّب على expiration_date
                if base == "expiry_date":
                    qs = qs.order_by(ordering.replace("expiry_date", "expiration_date"))

    # تصدير/طباعة قبل التقسيم لصفحات (على المجموعة المُفلترة كاملة)
    if "download_pdf" in request.GET:
        return render_to_pdf(
            "products/products_pdf.html",
            {"products": qs, "request": request},
            filename="finished_products.pdf",
            inline=True,
        )

    export = (request.GET.get("export") or "").lower()
    if export in {"excel", "xlsx", "csv", "json"} or fmt == "json":
        rows = []
        for p in qs:
            expiry = _coalesce_attr(p, "expiration_date", "expiry_date")
            status_disp = "-"
            # عرض الحالة المتوافقة
            if hasattr(p, "get_quality_status_display"):
                try:
                    status_disp = p.get_quality_status_display()
                except Exception:
                    pass
            elif hasattr(p, "get_status_display"):
                try:
                    status_disp = p.get_status_display()
                except Exception:
                    pass

            rows.append({
                "كود المنتج": getattr(p, "product_code", ""),
                "الاسم": getattr(p, "name", ""),
                "الكمية": getattr(p, "quantity", 0),
                "الحالة": status_disp,
                "تاريخ الإنتاج": _fmt_date(getattr(p, "date_produced", None)),
                "تاريخ الانتهاء": _fmt_date(expiry),
                "الأيام حتى الانتهاء": _safe_days_to_expiry(expiry),
            })

        if export in {"excel", "xlsx"}:
            columns = ["كود المنتج", "الاسم", "الكمية", "الحالة", "تاريخ الإنتاج", "تاريخ الانتهاء", "الأيام حتى الانتهاء"]
            return export_to_excel(rows, columns=columns, filename="finished_products.xlsx")
        if export == "json" or fmt == "json":
            return JsonResponse(rows, safe=False, json_dumps_params={"ensure_ascii": False})
        if export == "csv":
            resp = HttpResponse(content_type="text/csv; charset=utf-8")
            resp["Content-Disposition"] = 'attachment; filename="finished_products.csv"'
            w = csv.writer(resp)
            if rows:
                w.writerow(rows[0].keys())
                for r in rows:
                    w.writerow(r.values())
            else:
                w.writerow(["لا توجد بيانات"])
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
        "products": page_obj,  # Page قابل للتكرار
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
def product_create(request):
    if request.method == "POST":
        form = FinishedProductForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            try:
                messages.success(request, "تم إنشاء المنتج بنجاح.")
            except Exception:
                pass
            # إعادة التوجيه للقائمة الموحّدة
            return redirect("products:product_list")
    else:
        form = FinishedProductForm()
    return render(request, "products/product_form.html", {"form": form})


# ✏️ تعديل منتج
@require_http_methods(["GET", "POST"])
@login_required
def product_edit(request, pk):
    product = get_object_or_404(FinishedProduct, pk=pk)
    if request.method == "POST":
        form = FinishedProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            try:
                messages.success(request, "تم تعديل المنتج بنجاح.")
            except Exception:
                pass
            return redirect("products:product_list")
    else:
        form = FinishedProductForm(instance=product)
    return render(request, "products/product_form.html", {"form": form, "edit_mode": True})


# ❌ حذف منتج
@require_http_methods(["GET", "POST"])
@login_required
def product_delete(request, pk):
    product = get_object_or_404(FinishedProduct, pk=pk)
    if request.method == "POST":
        product.delete()
        try:
            messages.success(request, "تم حذف المنتج بنجاح.")
        except Exception:
            pass
        return redirect("products:product_list")
    return render(request, "products/product_confirm_delete.html", {"product": product})


from django.shortcuts import render

def index(request):
    return render(request, 'products/index.html')


def app_home(request):
    return render(request, 'apps/products/home.html', {'app': 'products'})
