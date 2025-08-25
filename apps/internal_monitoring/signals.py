from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import RiskIncident, DisciplinaryAction
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.alerts import trigger_risk_alert

# ✅ 1. إشعار عند تسجيل حادث مخاطرة
@receiver(post_save, sender=RiskIncident)
def handle_risk_incident(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.user
    risk = instance.risk_level
    event = instance.event_type
    notes = instance.notes or ""

    # ✅ تنبيه الذكاء الاصطناعي (حقول مطابقة للموديل)
    AIDecisionAlert.objects.create(
        title=f"حادث مخاطرة ({risk})",
        description=f"الحدث: {event}\nالمستخدم: {user.username if user else 'غير معروف'}\nملاحظات: {notes}"
    )

    # 🔔 تنبيه عالي المخاطر
    if risk == "HIGH":
        trigger_risk_alert(event=event, user=user, risk_level=risk, note=notes)

        # ⛔ تعطيل المستخدم
        if user:
            user.is_active = False
            user.save()

# ✅ 2. إشعار عند تسجيل إجراء تأديبي
@receiver(post_save, sender=DisciplinaryAction)
def discipline_alert(sender, instance, **kwargs):
    if getattr(instance, "type", "") == "warning":
        AIDecisionAlert.objects.create(
            title="تحذير تأديبي",
            description=f"تحذير تأديبي للموظف {getattr(instance.employee, 'name', 'غير معروف')}."
        )
