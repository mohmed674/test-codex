# ERP_CORE/voice_commands/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VoiceCommand
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident

@receiver(post_save, sender=VoiceCommand)
def alert_ai_on_voice_command(sender, instance, created, **kwargs):
    if created:
        # ✅ 1. تنبيه الذكاء الاصطناعي
        AIDecisionAlert.objects.create(
            section='voice_commands',
            alert_type='أمر صوتي جديد',
            message=f"تم رفع أمر صوتي بواسطة {instance.user}",
            level='info'
        )

        # ✅ 2. تسجيل في سجل المراقبة الذكي (لأغراض تحليل أمني أو إساءة استخدام)
        RiskIncident.objects.create(
            user=instance.user,
            category='Voice',
            event_type='رفع أمر صوتي',
            risk_level='LOW',
            notes='تم تسجيل أمر صوتي جديد، جارٍ تحليله من قبل الذكاء الاصطناعي'
        )
