from .models import BehaviorLog
from apps.ai_decision.models import AIDecisionAlert
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=BehaviorLog)
def monitor_behavior(sender, instance, **kwargs):
    if instance.score < 5:
        AIDecisionAlert.objects.create(
            section="employee_monitoring",
            message=f"🧠 سلوك غير معتاد من {instance.employee.name} (تقييم: {instance.score})"
        )