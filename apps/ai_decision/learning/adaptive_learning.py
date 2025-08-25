from datetime import timedelta, date, datetime
from collections import Counter
from apps.attendance.models import Attendance
from apps.evaluation.models import Evaluation
from apps.clients.models import Client
from apps.ai_decision.models import DecisionAnalysis

# 🔁 التعلم الذاتي من التطبيقات الأخرى

def learn_from_attendance():
    recent_data = Attendance.objects.filter(date__gte=date.today() - timedelta(days=30))
    status_distribution = Counter(recent_data.values_list('status', flat=True))
    return {
        "pattern": "attendance",
        "insight": f"📊 نمط الحضور خلال آخر 30 يومًا: {dict(status_distribution)}"
    }

def learn_from_evaluations():
    evals = Evaluation.objects.filter(created_at__gte=date.today() - timedelta(days=30))
    try:
        avg_score = evals.aggregate_score()  # تأكد أن هذه الدالة موجودة داخل EvaluationManager
    except:
        avg_score = "❓ غير متاح (يجب توفير دالة حساب المتوسط)"
    return {
        "pattern": "performance",
        "insight": f"📈 متوسط تقييم الأداء: {avg_score}"
    }

def learn_from_clients():
    active_clients = Client.objects.filter(is_active=True).count()
    high_value = Client.objects.filter(total_purchases__gt=20000).count()
    return {
        "pattern": "clients",
        "insight": f"👥 {active_clients} عملاء نشطين – {high_value} منهم كبار المشترين"
    }

# 🔎 تحليل قرارات الذكاء الاصطناعي السابقة

def analyze_recent_decisions():
    recent_data = DecisionAnalysis.objects.filter(created_at__gte=datetime.today() - timedelta(days=30))
    patterns = []

    for decision in recent_data:
        if decision.accuracy >= 0.9 and "شراء" in decision.description:
            patterns.append("✅ قرارات الشراء المدعومة بالبيانات دقيقة جداً.")
        elif decision.accuracy < 0.6:
            patterns.append(f"⚠️ قرار مشكوك فيه: {decision.description} - الدقة {decision.accuracy * 100:.1f}%")
    
    if not patterns:
        patterns.append("📊 لا توجد أنماط واضحة حالياً.")
    
    return patterns

# 🧠 دمج كل الرؤى لعرضها في لوحة القيادة

def get_all_insights():
    insights = [
        learn_from_attendance(),
        learn_from_evaluations(),
        learn_from_clients()
    ]
    decision_patterns = analyze_recent_decisions()
    for item in decision_patterns:
        insights.append({"pattern": "decisions", "insight": item})
    return insights
