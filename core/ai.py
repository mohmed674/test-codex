# ✅ ERP_CORE/core/ai.py
from apps.ai_decision.models import AIDecisionAlert
from .models import EvaluationCriteria, ProductionStageType

def detect_missing_configurations():
    """كشف النواقص الحيوية في التكوين الأساسي وإرسال تنبيهات ذكية"""

    # 🔍 تحقق من وجود معايير تقييم
    if EvaluationCriteria.objects.count() == 0:
        AIDecisionAlert.objects.create(
            section='core',
            alert_type='نقص في إعدادات التقييم',
            level='warning',
            message="⚠️ لا توجد معايير تقييم معرفة داخل النظام. الرجاء إنشاء واحدة لضمان عمل نظام الأداء."
        )

    # 🔍 تحقق من وجود مراحل إنتاج
    if ProductionStageType.objects.count() == 0:
        AIDecisionAlert.objects.create(
            section='core',
            alert_type='نقص مراحل الإنتاج',
            level='warning',
            message="⚠️ لا توجد مراحل إنتاج معرفة في النظام. الرجاء مراجعة إعدادات التصنيع."
        )
