# ERP_CORE/voice_commands/ai.py
from apps.ai_decision.models import AIDecisionAlert
from .models import VoiceCommandLog

def detect_failed_commands():
    for cmd in VoiceCommandLog.objects.all():
        if cmd.result == 'Failed':
            AIDecisionAlert.objects.create(
                section='voice_commands',
                alert_type='فشل أمر صوتي',
                level='warning',
                message=f"فشل في التعرف على الأمر الصوتي للمستخدم {cmd.user}."
            )