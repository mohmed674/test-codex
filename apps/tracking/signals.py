# ERP_CORE/tracking/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Shipment
from apps.ai_decision.models import AIDecisionAlert
from apps.internal_monitoring.models import RiskIncident
from django.contrib.auth.models import User

@receiver(post_save, sender=Shipment)
def alert_ai_on_shipment_status(sender, instance, created, **kwargs):
    if instance.status == 'delayed':
        # ✅ 1. تنبيه الذكاء الاصطناعي
        AIDecisionAlert.objects.create(
            section='tracking',
            alert_type='تأخير شحنة',
            message=f"الشحنة رقم {instance.tracking_code} تأخرت عن موعدها المتوقع.",
            level='warning'
        )

        # ✅ 2. تسجيل مخالفة ذكية في نظام المراقبة
        RiskIncident.objects.create(
            user=User.objects.filter(is_superuser=True).first(),
            category='Stock',
            event_type='تأخير في الشحن',
            risk_level='MEDIUM',
            notes=f"تأخرت الشحنة رقم {instance.tracking_code} في التسليم"
        )
