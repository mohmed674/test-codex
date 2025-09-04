from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.ai_decision.models import AIDecisionAlert

from .models import Salary


@receiver(post_save, sender=Salary)
def salary_ai_check(sender, instance, **kwargs):
    if instance.amount < 2000:
        AIDecisionAlert.objects.create(
            section="payroll",
            message=f"💰 راتب منخفض للموظف {instance.employee.name} ({instance.amount} ج.م).",
        )
