from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.ai_decision.models import AIDecisionAlert

from .models import Employee


@receiver(post_save, sender=Employee)
def onboarding_ai_check(sender, instance, **kwargs):
    if instance.contract_type == "temporary":
        AIDecisionAlert.objects.create(
            section="employees",
            message=f"📝 موظف بعقد مؤقت: {instance.name} - راجع توزيع المهام.",
        )
