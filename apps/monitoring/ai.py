from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.ai_decision.models import AIDecisionAlert

from .models import Observation


@receiver(post_save, sender=Observation)
def observation_alert(sender, instance, **kwargs):
    if instance.notes and "خطر" in instance.notes:
        AIDecisionAlert.objects.create(
            section="monitoring", message=f"🔍 ملاحظة تتضمن خطر في {instance.location}."
        )
