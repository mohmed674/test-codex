from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.ai_decision.models import AIDecisionAlert

from .models import Evaluation


@receiver(post_save, sender=Evaluation)
def performance_check(sender, instance, **kwargs):
    if instance.total_score < 50:
        AIDecisionAlert.objects.create(
            section="evaluation",
            message=f"📉 تقييم منخفض لـ {instance.employee.name}: {instance.total_score}%",
        )
