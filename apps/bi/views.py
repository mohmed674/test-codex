# D:\ERP_CORE\bi\views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import FieldError
from django.template.exceptions import TemplateDoesNotExist
from django.apps import apps
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from io import StringIO
import csv

# ==================== Helpers ====================

def get_model(app_label: str, model_name: str):
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None

def _html(title, body):
    return f"""<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title></head>
<body style="font-family: system-ui, -apple-system, Segoe UI, Roboto; direction: rtl; padding: 16px">
{body}
</body></html>"""

def _safe_sum(qs, field='amount'):
    try:
        return qs.aggregate(total=Sum(field)).get('total') or 0
    except Exception:
        return 0

def _first_ok_aggregation(model, date_fields, amount_fields):
    """
    يحاول عمل تجميع شهري باستخدام أول تركيبة حقول صحيحة.
    يرجع (queryset, month_key) أو ([], None) عند الفشل.
    """
    if not model:
        return [], None
    for d in date_fields:
        for a in amount_fields:
            try:
                qs = (
                    model.objects.values(f"{d}__month")
                    .annotate(total=Sum(a))
                    .order_by(f"{d}__month")
                )
                return qs, f"{d}__month"
            except Exception:
                continue
    return [], None

# ==================== Exports ====================

def export_bi_pdf(request):
    SaleInvoice = get_model('sales', 'SaleInvoice') or get_model('sales', 'SaleOrder')
    data, month_key = _first_ok_aggregation(
        SaleInvoice,
        date_fields=['date_issued', 'date', 'created_at', 'issued_at'],
        amount_fields=['total_amount', 'total', 'amount', 'grand_total'],
    )
    context = {'data': data, 'date': timezone.now(), 'month_key': month_key or 'month'}
    try:
        from core.utils.export_utils import render_to_pdf  # type: ignore
        return render_to_pdf('bi/pdf_template.html', context)
    except Exception:
        try:
            return render(request, 'bi/pdf_template.html', context)
        except TemplateDoesNotExist:
            rows = []
            for r in data:
                rows.append(
                    f"<tr><td>{r.get(month_key) if month_key else ''}</td><td>{r.get('total') or 0}</td></tr>"
                )
            body = [
                "<h1>تقرير BI (عرض HTML بديل)</h1>",
                "<table border='1' cellpadding='6' cellspacing='0'>",
                "<thead><tr><th>الشهر</th><th>إجمالي المبيعات</th></tr></thead><tbody>",
                "".join(rows),
                "</tbody></table>",
            ]
            return HttpResponse(_html("تقرير BI", "".join(body)))

def export_bi_excel(request):
    SaleInvoice = get_model('sales', 'SaleInvoice') or get_model('sales', 'SaleOrder')
    data, month_key = _first_ok_aggregation(
        SaleInvoice,
        date_fields=['date_issued', 'date', 'created_at', 'issued_at'],
        amount_fields=['total_amount', 'total', 'amount', 'grand_total'],
    )
    try:
        from core.utils.export_utils import export_to_excel  # type: ignore
        values = [(r.get(month_key), r.get('total') or 0) for r in data]
        columns = ['الشهر', 'إجمالي المبيعات']
        return export_to_excel(values, columns, filename='bi_report.xlsx')
    except Exception:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['الشهر', 'إجمالي المبيعات'])
        for r in data:
            writer.writerow([r.get(month_key), r.get('total') or 0])
        resp = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = 'attachment; filename="bi_report.csv"'
        return resp

# ==================== Views ====================

def dashboard(request):
    SaleInvoice = get_model('sales', 'SaleInvoice') or get_model('sales', 'SaleOrder')
    JournalEntry = get_model('accounting', 'JournalEntry')
    Client = get_model('clients', 'Client')

    # مبيعات آخر 30 يوم (حاول مع عدة أسماء حقول) — كسر نظيف للحلقات
    recent_total = 0
    if SaleInvoice:
        date_fields = ['date_issued', 'date', 'created_at', 'issued_at']
        amount_fields = ['total_amount', 'total', 'amount', 'grand_total']
        found = False
        for d in date_fields:
            if found:
                break
            for a in amount_fields:
                try:
                    recent_total = (
                        SaleInvoice.objects
                        .filter(**{f"{d}__gte": timezone.now() - timedelta(days=30)})
                        .aggregate(total=Sum(a))
                        .get('total') or 0
                    )
                    found = True
                    break
                except Exception:
                    continue

    # الإيرادات/المصروفات
    revenue_val = 0
    expense_val = 0
    if JournalEntry:
        try:
            revenue_val = _safe_sum(JournalEntry.objects.filter(entry_type__iexact='credit'))
            expense_val = _safe_sum(JournalEntry.objects.filter(entry_type__iexact='debit'))
        except Exception:
            revenue_val = _safe_sum(JournalEntry.objects.filter(amount__gt=0))
            expense_val = abs(_safe_sum(JournalEntry.objects.filter(amount__lt=0)))

    ctx = {
        'recent_sales': recent_total,
        'client_count': Client.objects.count() if Client else 0,
        'revenue': revenue_val,
        'expense': expense_val,
    }
    try:
        return render(request, 'bi/dashboard.html', ctx)
    except TemplateDoesNotExist:
        body = f"""
<h1 style="margin:0 0 12px">لوحة البيانات (عرض بديل)</h1>
<ul>
  <li>مبيعات آخر 30 يوم: <strong>{ctx['recent_sales']}</strong></li>
  <li>عدد العملاء: <strong>{ctx['client_count']}</strong></li>
  <li>الإيرادات: <strong>{ctx['revenue']}</strong></li>
  <li>المصروفات: <strong>{ctx['expense']}</strong></li>
</ul>
<p style="opacity:.7">أضف القالب <code>bi/dashboard.html</code> لاحقًا لتحسين العرض.</p>
"""
        return HttpResponse(_html("لوحة BI", body))

def sales_analytics(request):
    SaleInvoice = get_model('sales', 'SaleInvoice') or get_model('sales', 'SaleOrder')
    data, month_key = _first_ok_aggregation(
        SaleInvoice,
        date_fields=['date_issued', 'date', 'created_at', 'issued_at'],
        amount_fields=['total_amount', 'total', 'amount', 'grand_total'],
    )
    try:
        return render(request, 'bi/sales_analytics.html', {'data': data, 'month_key': month_key})
    except TemplateDoesNotExist:
        rows = "".join(
            f"<tr><td>{r.get(month_key)}</td><td>{r.get('total') or 0}</td></tr>"
            for r in data
        )
        body = f"""
<h1>تحليلات المبيعات (بديل)</h1>
<table border="1" cellpadding="6" cellspacing="0">
  <thead><tr><th>الشهر</th><th>إجمالي المبيعات</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
"""
        return HttpResponse(_html("تحليلات المبيعات", body))

def client_analytics(request):
    Client = get_model('clients', 'Client')
    data = []
    if Client:
        try:
            data = (
                Client.objects
                .values('source')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
        except FieldError:
            data = [{'source': 'all', 'count': Client.objects.count()}]
    try:
        return render(request, 'bi/client_analytics.html', {'data': data})
    except TemplateDoesNotExist:
        rows = "".join(
            f"<tr><td>{(r.get('source') or 'غير محدد')}</td><td>{r.get('count') or 0}</td></tr>"
            for r in data
        )
        body = f"""
<h1>تحليلات العملاء (بديل)</h1>
<table border="1" cellpadding="6" cellspacing="0">
  <thead><tr><th>المصدر</th><th>العدد</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
"""
        return HttpResponse(_html("تحليلات العملاء", body))

def financial_analytics(request):
    JournalEntry = get_model('accounting', 'JournalEntry')
    revenues = []
    expenses = []
    if JournalEntry:
        try:
            revenues = (
                JournalEntry.objects.filter(entry_type__iexact='credit')
                .values('date__month').annotate(total=Sum('amount'))
                .order_by('date__month')
            )
            expenses = (
                JournalEntry.objects.filter(entry_type__iexact='debit')
                .values('date__month').annotate(total=Sum('amount'))
                .order_by('date__month')
            )
        except Exception:
            revenues = (
                JournalEntry.objects.filter(amount__gt=0)
                .values('date__month').annotate(total=Sum('amount'))
                .order_by('date__month')
            )
            expenses = (
                JournalEntry.objects.filter(amount__lt=0)
                .values('date__month').annotate(total=Sum('amount'))
                .order_by('date__month')
            )
    ctx = {'revenues': revenues, 'expenses': expenses}
    try:
        return render(request, 'bi/financial_analytics.html', ctx)
    except TemplateDoesNotExist:
        rev_rows = "".join(
            f"<tr><td>{r['date__month']}</td><td>{r['total'] or 0}</td></tr>"
            for r in revenues
        )
        exp_rows = "".join(
            f"<tr><td>{r['date__month']}</td><td>{r['total'] or 0}</td></tr>"
            for r in expenses
        )
        body = f"""
<h1>التحليل المالي (بديل)</h1>
<h3>الإيرادات</h3>
<table border="1" cellpadding="6" cellspacing="0">
  <thead><tr><th>الشهر</th><th>الإجمالي</th></tr></thead>
  <tbody>{rev_rows}</tbody>
</table>
<h3>المصروفات</h3>
<table border="1" cellpadding="6" cellspacing="0">
  <thead><tr><th>الشهر</th><th>الإجمالي</th></tr></thead>
  <tbody>{exp_rows}</tbody>
</table>
"""
        return HttpResponse(_html("التحليل المالي", body))

def suggest_top_months(request):
    SaleInvoice = get_model('sales', 'SaleInvoice') or get_model('sales', 'SaleOrder')
    data, month_key = _first_ok_aggregation(
        SaleInvoice,
        date_fields=['date_issued', 'date', 'created_at', 'issued_at'],
        amount_fields=['total_amount', 'total', 'amount', 'grand_total'],
    )
    data = list(data)[:3] if data else []
    try:
        return render(request, 'bi/suggestions.html', {'data': data, 'month_key': month_key})
    except TemplateDoesNotExist:
        items = "".join(
            f"<li>الشهر {r.get(month_key)}: {r.get('total') or 0}</li>"
            for r in data
        )
        body = f"""
<h1>أفضل الأشهر (بديل)</h1>
<ol>{items}</ol>
"""
        return HttpResponse(_html("أفضل الأشهر", body))


from django.shortcuts import render

def index(request):
    return render(request, 'bi/index.html')


def app_home(request):
    return render(request, 'apps/bi/home.html', {'app': 'bi'})
