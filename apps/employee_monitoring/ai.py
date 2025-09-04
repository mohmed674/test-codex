# ERP_CORE/employee_monitoring/ai.py
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.ai_decision.models import AIDecisionAlert

# نحصل على الموديل ديناميكياً
BehaviorLog = apps.get_model("employee_monitoring", "BehaviorLog")


@receiver(post_save, sender=BehaviorLog)
def monitor_behavior(sender, instance, **kwargs):
    employee = getattr(instance, "employee", None)
    score = getattr(instance, "score", 0)

    if score < 5:
        AIDecisionAlert.objects.create(
            section="employee_monitoring",
            message=f"🧠 سلوك غير معتاد من {getattr(employee, 'name', 'موظف غير معروف')} (تقييم: {score})",
            level="warning",
        )
