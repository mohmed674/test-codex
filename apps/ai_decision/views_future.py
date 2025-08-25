from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
import random
import json
from typing import Dict, Any, List


# =========================
# 1) التحليل التنبؤي (عرض)
# =========================
def ai_predictive_analysis(request):
    """
    شاشة مبسطة للتحليل التنبؤي. لاحقاً نربطها بالبيانات الفعلية.
    يدعم اختيار نافذة زمنية عبر ?window_days=30 (اختياري).
    """
    window_days = 14
    try:
        window_days = int(request.GET.get("window_days", window_days))
    except Exception:
        pass

    future_risks = [
        {"type": "مبيعات",   "risk": f"انخفاض الطلب المتوقع خلال {window_days} يوم"},
        {"type": "إنتاج",    "risk": "زيادة استهلاك المواد الخام بنسبة 22%"},
        {"type": "عمالة",    "risk": "ارتفاع معدلات الغياب الأسبوع القادم"},
    ]
    return render(request, 'ai_decision/predictive_analysis.html', {
        'risks': future_risks,
        'window_days': window_days,
    })


# =========================================
# 2) API مساعد القرار (يدعم JSON و FormData)
# =========================================
def _classify_and_reply(query: str) -> Dict[str, Any]:
    """
    قواعد أولية بسيطة لتوليد توصية + قائمة قواعد متطابقة + درجة ثقة تقريبية.
    """
    q = query or ""
    rules: List[str] = []

    if "خصم" in q or "تخفيض" in q:
        rules.append("discount_review")
    if "توسعة" in q or "فرع" in q or "افتتاح" in q:
        rules.append("expansion")
    if ("سعر" in q) and ("رفع" in q or "زيادة" in q):
        rules.append("price_increase")
    if "مخزون" in q and ("نفاد" in q or "منخفض" in q or "عجز" in q):
        rules.append("stock_risk")
    if "توظيف" in q or "تعيين" in q or "موظفين" in q:
        rules.append("hiring")
    if "مورد" in q and ("تأخير" in q or "متأخر" in q):
        rules.append("supplier_delay")

    if "discount_review" in rules:
        rec = "⚠️ يُنصح بمراجعة أسباب الخصومات وتحديد حد أدنى للهامش."
    elif "expansion" in rules:
        rec = "📈 خطوة التوسعة موفقة بشرط توافر الموارد وخطة تشغيل واضحة."
    elif "price_increase" in rules:
        rec = "💹 رفع الأسعار ممكن، ادرس حساسية الطلب وحدّث سياسات الخصم."
    elif "stock_risk" in rules:
        rec = "📦 راقب المخزون وقم بإعادة الطلب مبكرًا لمنع نفاد الصنف."
    elif "hiring" in rules:
        rec = "👥 التوظيف مناسب إذا كان العائد المتوقع يغطي التكلفة خلال 3–6 أشهر."
    elif "supplier_delay" in rules:
        rec = "⏱️ فعّل تقييم المزودين وأضف غرامات تأخير في العقود."
    else:
        rec = "✅ القرار يبدو مناسبًا حسب المعطيات المتاحة."

    # درجة ثقة تقريبية بناءً على عدد القواعد المتطابقة (للاستخدام المبدئي)
    confidence = min(0.9, 0.5 + 0.1 * len(rules))

    return {
        "recommendation": rec,
        "matched_rules": rules,
        "confidence": round(confidence, 2),
    }


@csrf_exempt
@require_POST
def ai_decision_assistant_api(request):
    """
    يستقبل POST كـ form-data (query=...) أو JSON {"query": "..."} ويعيد توصية.
    """
    query = request.POST.get("query")
    if query is None:
        # محاولة قراءة JSON
        try:
            payload = json.loads(request.body or "{}")
            query = payload.get("query", "")
        except json.JSONDecodeError:
            query = ""

    result = _classify_and_reply(query)
    return JsonResponse({
        "timestamp": timezone.now().isoformat(),
        "query": query,
        **result
    })


# =========================================
# 3) لوحة بصرية مبسطة (بيانات تجريبية)
# =========================================
def ai_visual_dashboard(request):
    """
    يولّد بيانات عشوائية خفيفة لعرض تنبيهات/اقتراحات برسومات.
    يدعم seed اختياري عبر ?seed=123 لتثبيت النتائج أثناء الاختبار.
    """
    try:
        seed = int(request.GET.get("seed", "0"))
    except Exception:
        seed = 0
    if seed:
        random.seed(seed)

    labels = ["مبيعات", "إنتاج", "صيانة", "موارد بشرية"]
    chart_data = {
        "labels": labels,
        "alerts": [random.randint(1, 10) for _ in labels],
        "suggestions": [random.randint(0, 5) for _ in labels],
    }
    return render(request, 'ai_decision/visual_dashboard.html', {
        "chart_data": chart_data
    })


# ================================
# 4) لوحة التعلم (عرض بسيط حالياً)
# ================================
def ai_learning_dashboard(request):
    return render(request, 'ai_decision/learning_dashboard.html')
