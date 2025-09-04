"""AI Decision views: dashboard, reports, exports, and copilot endpoints."""

from __future__ import annotations

import csv
from datetime import timedelta

from django.contrib import messages
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import TemplateDoesNotExist, get_template
from django.utils import timezone
from django.utils.html import escape
from django.utils.translation import gettext as _

from apps.accounting.models import PurchaseInvoice
from apps.sales.models import SaleInvoice, SaleItem

from .forms import DecisionAnalysisForm
from .models import DecisionAnalysis

# ---- Helpers ---------------------------------------------------------------


def _model_has_field(Model, field_name: str) -> bool:
    """Return True if Model has a field named `field_name`."""
    try:
        return any(f.name == field_name for f in Model._meta.get_fields())
    except Exception:  # pragma: no cover - very defensive
        return False


def _sum(qs, field: str = "total_amount"):
    """Aggregate sum on queryset field with safe fallback."""
    try:
        return qs.aggregate(total=Sum(field)).get("total") or 0
    except Exception:  # pragma: no cover
        return 0


def _sales_date_field() -> str:
    """Prefer `date_issued` if exists, else fallback to `date`."""
    if _model_has_field(SaleInvoice, "date_issued"):
        return "date_issued"
    return "date"


def _build_ai_dashboard_context():
    """Compose dashboard context (recent sales, top products, delays, insights)."""
    today = timezone.now()
    last_30 = today - timedelta(days=30)

    date_field = _sales_date_field()
    date_filter = {f"{date_field}__gte": last_30}

    recent_total_sales = (
        SaleInvoice.objects.filter(**date_filter)
        .aggregate(total=Sum("total_amount"))
        .get("total")
        or 0
    )

    top_products = (
        SaleItem.objects.values("product__name")
        .annotate(qty=Sum("quantity"))
        .order_by("-qty")[:5]
    )

    if _model_has_field(PurchaseInvoice, "is_delayed"):
        delayed_suppliers = (
            PurchaseInvoice.objects.filter(is_delayed=True)
            .values("supplier__name")
            .annotate(delays=Count("id"))
            .order_by("-delays")[:5]
        )
    else:
        delayed_suppliers = (
            PurchaseInvoice.objects.values("supplier__name")
            .annotate(delays=Count("id"))
            .order_by("-delays")[:5]
        )

    alerts: list[str] = []
    suggestions: list[str] = []

    if recent_total_sales == 0:
        alerts.append(_("لا توجد مبيعات آخر 30 يوم."))
        suggestions.append(_("تحقق من حالة نقاط البيع وقنوات الطلبات."))

    if top_products:
        best = top_products[0]
        suggestions.append(
            _("ركّز على توفير المخزون للمنتج الأعلى مبيعًا: {name}.").format(
                name=best["product__name"]
            )
        )

    if delayed_suppliers:
        worst = delayed_suppliers[0]
        alerts.append(
            _("تأخيرات متكررة من المورد: {supplier} ({count} مرة).").format(
                supplier=worst["supplier__name"], count=worst["delays"]
            )
        )
        suggestions.append(_("راجع شروط التوريد أو أضف موردًا بديلًا."))

    return {
        "total_sales": recent_total_sales,
        "top_products": top_products,
        "delayed_suppliers": delayed_suppliers,
        "alerts": alerts,
        "suggestions": suggestions,
        "generated_at": today,
    }


# ---- Views -----------------------------------------------------------------


def analyze_decision(request):
    form = DecisionAnalysisForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("✅ تم حفظ تحليل القرار بنجاح."))
        return redirect("analyze_decision")
    return render(request, "ai_decision/analyze_decision.html", {"form": form})


def decision_report(request):
    decisions = DecisionAnalysis.objects.select_related("employee").order_by(
        "-created_at"
    )
    return render(request, "ai_decision/report.html", {"decisions": decisions})


def decision_history_view(request):
    decisions = DecisionAnalysis.objects.select_related("employee").order_by(
        "-created_at"
    )
    return render(
        request,
        "ai_decision/decision_history.html",
        {"decisions": decisions},
    )


def ai_report_pdf(request):
    ctx = _build_ai_dashboard_context()
    try:
        html = get_template("ai_decision/ai_report_pdf.html").render(ctx)
    except TemplateDoesNotExist:
        alerts_html = "".join(f"<li>{escape(a)}</li>" for a in ctx["alerts"])
        sugg_html = "".join(f"<li>{escape(s)}</li>" for s in ctx["suggestions"])
        html = (
            "<h1>تقرير الذكاء الاصطناعي</h1>"
            f"<p>تاريخ الإنشاء: {ctx['generated_at']:%Y-%m-%d %H:%M}</p>"
            "<h3>ملخص</h3>"
            f"<ul><li>إجمالي مبيعات آخر 30 يوم: {ctx['total_sales']}</li></ul>"
            f"<h3>تنبيهات</h3><ul>{alerts_html or '<li>لا يوجد</li>'}</ul>"
            f"<h3>اقتراحات</h3><ul>{sugg_html or '<li>لا يوجد</li>'}</ul>"
        )

    try:
        from weasyprint import HTML  # local import to avoid hard dependency

        pdf_file = HTML(string=html).write_pdf()
        resp = HttpResponse(pdf_file, content_type="application/pdf")
        resp["Content-Disposition"] = 'attachment; filename="ai_report.pdf"'
        return resp
    except Exception:
        # Fallback: deliver HTML directly
        return HttpResponse(html)


def ai_report_excel(request):
    ctx = _build_ai_dashboard_context()
    rows = []
    rows += [{"نوع": _("تنبيه"), "النص": a} for a in ctx["alerts"]]
    rows += [{"نوع": _("اقتراح"), "النص": s} for s in ctx["suggestions"]]

    try:
        from core.utils.export_utils import export_to_excel  # type: ignore

        return export_to_excel(
            rows,
            columns=["نوع", "النص"],
            filename="ai_report.xlsx",
        )
    except Exception:
        # CSV fallback if Excel exporter unavailable
        output = ["نوع,النص"]
        output.extend(f"{r['نوع']},{r['النص']}" for r in rows)
        resp = HttpResponse("\n".join(output), content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="ai_report.csv"'
        return resp


def ai_report_csv(request):
    ctx = _build_ai_dashboard_context()
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="ai_report.csv"'
    writer = csv.writer(response)
    writer.writerow(["النوع", "النص"])
    for alert in ctx["alerts"]:
        writer.writerow(["تنبيه", alert])
    for suggestion in ctx["suggestions"]:
        writer.writerow(["اقتراح", suggestion])
    return response


def ai_dashboard(request):
    ctx = _build_ai_dashboard_context()
    return render(request, "ai_decision/dashboard.html", ctx)


def ai_reports_dashboard(request):
    ctx = _build_ai_dashboard_context()
    return render(request, "ai_decision/dashboard.html", ctx)


def ai_sales_analysis_report(request):
    date_field = _sales_date_field()
    this_month = timezone.now().date().replace(day=1)
    filt = {f"{date_field}__gte": this_month}
    series = (
        SaleInvoice.objects.filter(**filt)
        .values(f"{date_field}__day")
        .annotate(total=Sum("total_amount"))
        .order_by(f"{date_field}__day")
    )
    return render(
        request,
        "ai_decision/sales_analysis_report.html",
        {"series": series},
    )


def copilot_view(request):
    ctx = _build_ai_dashboard_context()
    return render(request, "ai_decision/copilot.html", ctx)


def copilot_query(request):
    q = (request.GET.get("query") or "").lower()
    today = timezone.now()
    last_week = today - timedelta(days=7)

    date_field = _sales_date_field()
    filt = {f"{date_field}__gte": last_week}

    if ("مبيعات" in q and "أسبوع" in q) or ("sales" in q and "week" in q):
        total = (
            SaleInvoice.objects.filter(**filt)
            .aggregate(total=Sum("total_amount"))
            .get("total")
            or 0
        )
        reply = _("✅ مبيعات هذا الأسبوع: {amount}").format(amount=f"{total:.2f}")

    elif ("أكثر" in q and "مبيع" in q) or ("top" in q and "products" in q):
        top = (
            SaleItem.objects.values("product__name")
            .annotate(qty=Sum("quantity"))
            .order_by("-qty")[:5]
        )
        if top:
            header = _("★ أكثر 5 منتجات مبيعاً:")
            lines = [
                _("{name} - {qty} وحدة").format(
                    name=p["product__name"],
                    qty=p["qty"],
                )
                for p in top
            ]
            reply = f"{header}\n" + "\n".join(lines)
        else:
            reply = _("لا توجد بيانات حالياً.")

    elif ("مورد" in q and "تأخير" in q) or ("supplier" in q and "delay" in q):
        if _model_has_field(PurchaseInvoice, "is_delayed"):
            delayed = (
                PurchaseInvoice.objects.filter(is_delayed=True)
                .values("supplier__name")
                .annotate(delays=Count("id"))
                .order_by("-delays")
            )
        else:
            delayed = (
                PurchaseInvoice.objects.values("supplier__name")
                .annotate(delays=Count("id"))
                .order_by("-delays")
            )
        if delayed:
            header = _("🚤 الموردون المتأخرون:")
            lines = [
                _("{name} - {count} مرة").format(
                    name=s["supplier__name"],
                    count=s["delays"],
                )
                for s in delayed[:5]
            ]
            reply = f"{header}\n" + "\n".join(lines)
        else:
            reply = _("لا يوجد تأخير من الموردين حالياً.")

    else:
        reply = _("❌ لم أفهم سؤالك. استخدم الأزرار أو اكتب صيغة واضحة.")

    return HttpResponse(escape(reply))


def index(request):
    return render(request, "ai_decision/index.html")


def app_home(request):
    return render(request, "apps/ai_decision/home.html", {"app": "ai_decision"})
