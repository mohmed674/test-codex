# ERP_CORE/core/ai.py
from typing import Final

from apps.ai_decision.models import AIDecisionAlert

from .models import EvaluationCriteria, ProductionStageType

# ثوابت لتفادي السلاسل المكررة وتحسين القراءة
_CORE_SECTION: Final[str] = "core"


def detect_missing_configurations() -> None:
    """كشف النواقص الحيوية في التكوين الأساسي وإرسال تنبيهات ذكية."""
    # 🔍 تحقق من وجود معايير تقييم
    if EvaluationCriteria.objects.count() == 0:
        AIDecisionAlert.objects.create(
            section=_CORE_SECTION,
            alert_type="نقص في إعدادات التقييم",
            level="warning",
            message=(
                "⚠️ لا توجد معايير تقييم معرفة داخل النظام. الرجاء إنشاء واحدة "
                "لضمان عمل نظام الأداء."
            ),
        )

    # 🔍 تحقق من وجود مراحل إنتاج
    if ProductionStageType.objects.count() == 0:
        AIDecisionAlert.objects.create(
            section=_CORE_SECTION,
            alert_type="نقص مراحل الإنتاج",
            level="warning",
            message=(
                "⚠️ لا توجد مراحل إنتاج معرفة في النظام. الرجاء مراجعة إعدادات التصنيع."
            ),
        )
