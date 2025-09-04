from __future__ import annotations

from collections import Counter
from datetime import timedelta
from typing import Any, Dict, List

from django.utils import timezone
from django.utils.translation import gettext as _

from apps.ai_decision.models import DecisionAnalysis
from apps.attendance.models import Attendance
from apps.clients.models import Client
from apps.evaluation.models import Evaluation


# 🔁 التعلم الذاتي من التطبيقات الأخرى
def learn_from_attendance() -> Dict[str, Any]:
    since = timezone.now().date() - timedelta(days=30)
    recent_data = Attendance.objects.filter(date__gte=since)
    statuses: List[str] = list(recent_data.values_list("status", flat=True))
    status_distribution = Counter(statuses)

    return {
        "pattern": "attendance",
        "insight": _("📊 نمط الحضور خلال آخر 30 يومًا: {dist}").format(
            dist=dict(status_distribution)
        ),
    }


def learn_from_evaluations() -> Dict[str, Any]:
    since_dt = timezone.now() - timedelta(days=30)
    evals = Evaluation.objects.filter(created_at__gte=since_dt)

    avg_score: Any = None
    agg = getattr(evals, "aggregate_score", None)
    if callable(agg):
        try:
            avg_score = agg()
        except Exception:
            avg_score = None

    if isinstance(avg_score, (int, float)):
        score_text = f"{avg_score:.2f}"
    else:
        score_text = _("❓ غير متاح (يجب توفير دالة حساب المتوسط)")

    return {
        "pattern": "performance",
        "insight": _("📈 متوسط تقييم الأداء: {score}").format(score=score_text),
    }


def learn_from_clients() -> Dict[str, Any]:
    active_clients = Client.objects.filter(is_active=True).count()
    high_value = Client.objects.filter(total_purchases__gt=20000).count()
    return {
        "pattern": "clients",
        "insight": _("👥 {active} عملاء نشطين – {vip} منهم كبار المشترين").format(
            active=active_clients, vip=high_value
        ),
    }


# 🔎 تحليل قرارات الذكاء الاصطناعي السابقة
def analyze_recent_decisions() -> List[str]:
    since_dt = timezone.now() - timedelta(days=30)
    recent_data = DecisionAnalysis.objects.filter(created_at__gte=since_dt)

    patterns: List[str] = []
    for decision in recent_data:
        accuracy = float(getattr(decision, "accuracy", 0.0) or 0.0)
        desc = str(getattr(decision, "description", "") or "")

        if accuracy >= 0.9 and "شراء" in desc:
            patterns.append(_("✅ قرارات الشراء المدعومة بالبيانات دقيقة جداً."))
        elif accuracy < 0.6:
            patterns.append(
                _("⚠️ قرار مشكوك فيه: {desc} - الدقة {pct:.1f}%").format(
                    desc=desc, pct=accuracy * 100
                )
            )

    if not patterns:
        patterns.append(_("📊 لا توجد أنماط واضحة حالياً."))

    return patterns


# 🧠 دمج كل الرؤى لعرضها في لوحة القيادة
def get_all_insights() -> List[Dict[str, Any]]:
    insights = [
        learn_from_attendance(),
        learn_from_evaluations(),
        learn_from_clients(),
    ]
    for item in analyze_recent_decisions():
        insights.append({"pattern": "decisions", "insight": item})
    return insights
