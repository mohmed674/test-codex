# D:\ERP_CORE\ai_decision\views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template, TemplateDoesNotExist
from django.db.models import Sum, Count
from django.utils.html import escape

from datetime import timedelta, datetime
import csv

from .models import DecisionAnalysis, AIDecisionAlert
from .forms import DecisionAnalysisForm

from apps.sales.models import SaleInvoice, SaleItem
from apps.products.models import Product
from apps.accounting.models import PurchaseInvoice


def _model_has_field(Model, field_name: str) -> bool:
    try:
        return any(f.name == field_name for f in Model._meta.get_fields())
    except Exception:
        return False


def _sum(qs, field='total_amount'):
    try:
        return qs.aggregate(total=Sum(field)).get('total') or 0
    except Exception:
        return 0


def _sales_date_field():
    if _model_has_field(SaleInvoice, 'date_issued'):
        return 'date_issued'
    return 'date'


def _build_ai_dashboard_context():
    today = timezone.now()
    last_30 = today - timedelta(days=30)

    date_field = _sales_date_field()
    date_filter = {f"{date_field}__gte": last_30}

    recent_total_sales = (
        SaleInvoice.objects.filter(**date_filter)
        .aggregate(total=Sum("total_amount"))
        .get("total") or 0
    )

    top_products = (
        SaleItem.objects
        .values("product__name")
        .annotate(qty=Sum("quantity"))
        .order_by("-qty")[:5]
    )

    if _model_has_field(PurchaseInvoice, 'is_delayed'):
        delayed_suppliers = (
            PurchaseInvoice.objects
            .filter(is_delayed=True)
            .values("supplier__name")
            .annotate(delays=Count("id"))
            .order_by("-delays")[:5]
        )
    else:
        delayed_suppliers = (
            PurchaseInvoice.objects
            .values("supplier__name")
            .annotate(delays=Count("id"))
            .order_by("-delays")[:5]
        )

    alerts = []
    suggestions = []

    if recent_total_sales == 0:
        alerts.append("لا توجد مبيعات آخر 30 يوم.")
        suggestions.append("تحقق من حالة نقاط البيع وقنوات الطلبات.")

    if top_products:
        best = top_products[0]
        suggestions.append(f"ركّز على توفير المخزون للمنتج الأعلى مبيعًا: {best['product__name']}.")

    if delayed_suppliers:
        worst = delayed_suppliers[0]
        alerts.append(f"تأخيرات متكررة من المورد: {worst['supplier__name']} ({worst['delays']} مرة).")
        suggestions.append("راجع شروط التوريد أو أضف موردًا بديلًا.")

    return {
        "total_sales": recent_total_sales,
        "top_products": top_products,
        "delayed_suppliers": delayed_suppliers,
        "alerts": alerts,
        "suggestions": suggestions,
        "generated_at": today,
    }


def analyze_decision(request):
    form = DecisionAnalysisForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, '✅ تم حفظ تحليل القرار بنجاح.')
        return redirect('analyze_decision')
    return render(request, 'ai_decision/analyze_decision.html', {'form': form})


def decision_report(request):
    decisions = DecisionAnalysis.objects.select_related('employee').order_by('-created_at')
    return render(request, 'ai_decision/report.html', {'decisions': decisions})


def decision_history_view(request):
    decisions = DecisionAnalysis.objects.select_related('employee').order_by('-created_at')
    return render(request, 'ai_decision/decision_history.html', {'decisions': decisions})


def ai_report_pdf(request):
    ctx = _build_ai_dashboard_context()
    try:
        html = get_template('ai_decision/ai_report_pdf.html').render(ctx)
    except TemplateDoesNotExist:
        alerts_html = "".join(f"<li>{escape(a)}</li>" for a in ctx["alerts"])
        sugg_html = "".join(f"<li>{escape(s)}</li>" for s in ctx["suggestions"])
        html = f"""
        <h1>تقرير الذكاء الاصطناعي</h1>
        <p>تاريخ الإنشاء: {ctx['generated_at']:%Y-%m-%d %H:%M}</p>
        <h3>ملخص</h3>
        <ul>
            <li>إجمالي مبيعات آخر 30 يوم: {ctx['total_sales']}</li>
        </ul>
        <h3>تنبيهات</h3><ul>{alerts_html or "<li>لا يوجد</li>"}</ul>
        <h3>اقتراحات</h3><ul>{sugg_html or "<li>لا يوجد</li>"}</ul>
        """

    try:
        from weasyprint import HTML
        pdf_file = HTML(string=html).write_pdf()
        resp = HttpResponse(pdf_file, content_type="application/pdf")
        resp['Content-Disposition'] = 'attachment; filename="ai_report.pdf"'
        return resp
    except Exception:
        return HttpResponse(html)


def ai_report_excel(request):
    ctx = _build_ai_dashboard_context()
    rows = []
    rows += [{'نوع': 'تنبيه', 'النص': a} for a in ctx['alerts']]
    rows += [{'نوع': 'اقتراح', 'النص': s} for s in ctx['suggestions']]

    try:
        from core.utils.export_utils import export_to_excel  # type: ignore
        return export_to_excel(rows, columns=['نوع', 'النص'], filename='ai_report.xlsx')
    except Exception:
        output = []
        output.append("نوع,النص")
        for r in rows:
            output.append(f"{r['نوع']},{r['النص']}")
        resp = HttpResponse("\n".join(output), content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = 'attachment; filename="ai_report.csv"'
        return resp


def ai_report_csv(request):
    ctx = _build_ai_dashboard_context()
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="ai_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['النوع', 'النص'])
    for alert in ctx['alerts']:
        writer.writerow(['تنبيه', alert])
    for suggestion in ctx['suggestions']:
        writer.writerow(['اقتراح', suggestion])
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
    return render(request, "ai_decision/sales_analysis_report.html", {"series": series})


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
            .get("total") or 0
        )
        reply = f"✅ مبيعات هذا الأسبوع: {total:.2f}"

    elif ("أكثر" in q and "مبيع" in q) or ("top" in q and "products" in q):
        top = (
            SaleItem.objects
            .values("product__name")
            .annotate(qty=Sum("quantity"))
            .order_by("-qty")[:5]
        )
        if top:
            reply = "★ أكثر 5 منتجات مبيعاً:\n" + "\n".join(
                [f"{p['product__name']} - {p['qty']} وحدة" for p in top]
            )
        else:
            reply = "لا توجد بيانات حالياً."

    elif ("مورد" in q and "تأخير" in q) or ("supplier" in q and "delay" in q):
        if _model_has_field(PurchaseInvoice, 'is_delayed'):
            delayed = (
                PurchaseInvoice.objects
                .filter(is_delayed=True)
                .values("supplier__name")
                .annotate(delays=Count("id"))
                .order_by("-delays")
            )
        else:
            delayed = (
                PurchaseInvoice.objects
                .values("supplier__name")
                .annotate(delays=Count("id"))
                .order_by("-delays")
            )
        if delayed:
            reply = "🚤 الموردون المتأخرون:\n" + "\n".join(
                [f"{s['supplier__name']} - {s['delays']} مرة" for s in delayed[:5]]
            )
        else:
            reply = "لا يوجد تأخير من الموردين حالياً."

    else:
        reply = "❌ لم أفهم سؤالك. استخدم الأزرار أو اكتب صيغة واضحة."

    return HttpResponse(escape(reply))


from django.shortcuts import render

def index(request):
    return render(request, 'ai_decision/index.html')


def app_home(request):
    return render(request, 'apps/ai_decision/home.html', {'app': 'ai_decision'})
