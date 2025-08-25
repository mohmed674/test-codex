from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from datetime import timedelta, datetime
from weasyprint import HTML
import csv
from django.utils.html import escape

from core.utils import export_to_excel
from .models import DecisionAnalysis, AIDecisionAlert
from .forms import DecisionAnalysisForm
from .ai_copilot_api import query_openai  # ✅ دمج OpenAI Copilot

# من تطبيقات أخرى
from apps.sales.models import SaleInvoice, SaleItem
from apps.products.models import Product
from apps.accounting.models import PurchaseInvoice
from django.db.models import Sum, Count

# ✅ 1. صفحة إدخال تحليل قرار يدوي
def analyze_decision(request):
    form = DecisionAnalysisForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, '✅ تم حفظ تحليل القرار بنجاح.')
        return redirect('analyze_decision')
    return render(request, 'ai_decision/analyze_decision.html', {'form': form})

# ✅ 2. تقرير القرارات المحللة
def decision_report(request):
    decisions = DecisionAnalysis.objects.select_related('employee').order_by('-created_at')
    return render(request, 'ai_decision/report.html', {'decisions': decisions})

# ✅ 3. سجل تحليلات القرارات السابقة
def decision_history_view(request):
    decisions = DecisionAnalysis.objects.select_related('employee').order_by('-created_at')
    return render(request, 'ai_decision/decision_history.html', {'decisions': decisions})

# ✅ 4. تصدير تقارير PDF
def ai_report_pdf(request):
    from .views_dashboard import ai_dashboard
    today = timezone.now().date()
    context = ai_dashboard(request).context_data
    html = get_template('ai_decision/ai_report_pdf.html').render(context)
    pdf_file = HTML(string=html).write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="ai_report_{today}.pdf"'
    return response

# ✅ 5. تصدير Excel
def ai_report_excel(request):
    from .views_dashboard import ai_dashboard
    today = timezone.now().date()
    context = ai_dashboard(request).context_data
    data = [{'نوع التنبيه': 'تنبيه', 'النص': alert} for alert in context['alerts']]
    data += [{'نوع التنبيه': 'اقتراح', 'النص': suggestion} for suggestion in context['suggestions']]
    return export_to_excel(data, filename=f'ai_report_{today}.xlsx')

# ✅ 6. تصدير CSV
def ai_report_csv(request):
    from .views_dashboard import ai_dashboard
    today = timezone.now().date()
    context = ai_dashboard(request).context_data
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ai_report_{today}.csv"'
    writer = csv.writer(response)
    writer.writerow(['النوع', 'النص'])
    for alert in context['alerts']:
        writer.writerow(['تنبيه', alert])
    for suggestion in context['suggestions']:
        writer.writerow(['اقتراح', suggestion])
    return response

# ✅ 7. لوحة القيادة
def ai_dashboard(request):
    return render(request, "ai_decision/dashboard.html")

# ✅ 8. نسخة أخرى من لوحة القيادة
def ai_reports_dashboard(request):
    return render(request, "ai_decision/dashboard.html")

# ✅ 9. تحليل مبيعات مخصص
def ai_sales_analysis_report(request):
    return render(request, "ai_decision/sales_analysis_report.html")

# ✅ 10. مساعد ERP الذكي (Copilot Assistant)
def copilot_view(request):
    # البيانات المرئية
    total_sales = SaleInvoice.objects.filter(date__month=timezone.now().month).aggregate(Sum("total_amount"))['total_amount__sum'] or 0
    top_products = SaleItem.objects.values("product__name").annotate(qty=Sum("quantity")).order_by("-qty")[:5]
    delayed_suppliers = PurchaseInvoice.objects.filter(is_delayed=True).values("supplier__name").annotate(delays=Count("id")).order_by("-delays")[:5]

    context = {
        "total_sales": total_sales,
        "top_products": top_products,
        "delayed_suppliers": delayed_suppliers,
    }
    return render(request, "ai_decision/copilot.html", context)

# ✅ 11. API رد ذكي متعدد المصادر (GPT + محلي)
def copilot_query(request):
    query = request.GET.get("query", "").strip()
    lowered = query.lower()
    today = datetime.today()
    last_week = today - timedelta(days=7)

    # منطق محلي
    if "مبيعات" in lowered and "أسبوع" in lowered:
        total = SaleInvoice.objects.filter(date__gte=last_week).aggregate(Sum("total_amount"))["total_amount__sum"]
        return JsonResponse({"reply": f"📦 إجمالي مبيعات هذا الأسبوع: {total:.2f} جنيه" if total else "لا توجد مبيعات في هذا الأسبوع."})

    elif "أكثر" in lowered and "مبيع" in lowered:
        top = SaleItem.objects.values("product__name").annotate(qty=Sum("quantity")).order_by("-qty")[:5]
        if top:
            response = "🏆 أكثر المنتجات مبيعاً:\n" + "\n".join([f"{p['product__name']} - {p['qty']} وحدة" for p in top])
        else:
            response = "لا توجد بيانات حالياً."
        return JsonResponse({"reply": response})

    elif "مورد" in lowered and "تأخير" in lowered:
        delayed = PurchaseInvoice.objects.filter(is_delayed=True).values("supplier__name").annotate(delays=Count("id")).order_by("-delays")
        if delayed:
            response = "🚚 الموردون المتأخرون:\n" + "\n".join([f"{s['supplier__name']} - {s['delays']} مرة" for s in delayed])
        else:
            response = "لا يوجد تأخير من الموردين حالياً."
        return JsonResponse({"reply": response})

    # استدعاء GPT لو لم يكن استعلام محلي
    reply = query_openai(query)
    return JsonResponse({"reply": escape(reply)})
