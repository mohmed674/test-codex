from .models import RiskIncident
from apps.ai_decision.models import AIDecisionAlert
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=RiskIncident)
def internal_risk_alert(sender, instance, **kwargs):
    if instance.severity == "high":
        AIDecisionAlert.objects.create(
            section="internal_monitoring",
            message=f"🚨 حادث مخاطرة حاد في {instance.department.name}."
        )