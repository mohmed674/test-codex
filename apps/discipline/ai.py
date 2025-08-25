# ERP_CORE/discipline/ai.py
from .models import DisciplineRecord
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

@receiver(post_save, sender=DisciplineRecord)
def analyze_disciplinary_action(sender, instance, created, **kwargs):
    if not created:
        return

    # إذا كانت العقوبة كبيرة (مثال: خصم أكثر من 200 جنيه)
    if instance.type == 'خصم' and instance.value >= 200:
        AIDecisionAlert.objects.create(
            section='discipline',
            alert_type='عقوبة كبيرة',
            message=f"⚠️ تم تسجيل خصم كبير للموظف {instance.employee.name}: {instance.value} جنيه",
            level='warning',
            timestamp=now()
        )
    
    # تنبيه في حال تعدد العقوبات لنفس الموظف خلال آخر 30 يومًا
    recent_count = DisciplineRecord.objects.filter(
        employee=instance.employee,
        date__gte=now().date().replace(day=1)  # هذا الشهر فقط
    ).count()

    if recent_count >= 3:
        AIDecisionAlert.objects.create(
            section='discipline',
            alert_type='تكرار العقوبات',
            message=f"🚨 الموظف {instance.employee.name} حصل على {recent_count} عقوبات هذا الشهر.",
            level='danger',
            timestamp=now()
        )

    # تسجيل مخالفة تنظيمية في النظام الداخلي
    RiskIncident.objects.create(
        user=instance.created_by,
        category="Discipline",
        event_type="تسجيل عقوبة",
        risk_level="MEDIUM" if instance.value >= 100 else "LOW",
        notes=f"📝 تم تسجيل {instance.type} للموظف {instance.employee.name}: {instance.reason}",
        reported_at=now()
    )
