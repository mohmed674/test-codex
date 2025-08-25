# ERP_CORE/tracking/ai.py
from apps.ai_decision.models import AIDecisionAlert
from .models import Shipment

def detect_late_delivery():
    from django.utils.timezone import now
    for shipment in Shipment.objects.all():
        if shipment.expected_delivery and shipment.expected_delivery < now().date() and shipment.status != 'Delivered':
            AIDecisionAlert.objects.create(
                section='tracking',
                alert_type='تأخير في الشحنة',
                level='warning',
                message=f"الشحنة {shipment.tracking_number} تأخرت عن الموعد المتوقع."
            )