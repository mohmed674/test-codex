# ERP_CORE/survey/ai.py
from apps.ai_decision.models import AIDecisionAlert
from .models import SurveyResponse

def detect_negative_feedback():
    for r in SurveyResponse.objects.all():
        if r.rating <= 2:
            AIDecisionAlert.objects.create(
                section='survey',
                alert_type='تقييم سلبي',
                level='warning',
                message=f"تقييم منخفض من {r.employee} - {r.comment}"
            )
