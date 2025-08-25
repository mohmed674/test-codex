# ERP_CORE/survey/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EmployeeSurvey
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident
from django.contrib.auth.models import User

@receiver(post_save, sender=EmployeeSurvey)
def alert_ai_on_survey_response(sender, instance, created, **kwargs):
    if created:
        # ✅ 1. تنبيه AI بوجود استبيان جديد
        AIDecisionAlert.objects.create(
            section='survey',
            alert_type='استبيان جديد',
            message=f"تم استبيان الموظف {instance.employee} بتقييم {instance.score}",
            level='info'
        )

        # ✅ 2. تسجيل مخالفة في حال كانت النتيجة منخفضة
        if instance.score < 30:
            RiskIncident.objects.create(
                user=User.objects.filter(is_superuser=True).first(),
                category='System',
                event_type='نتيجة استبيان منخفضة',
                risk_level='MEDIUM',
                notes=f"الموظف {instance.employee} حصل على تقييم منخفض = {instance.score}"
            )
