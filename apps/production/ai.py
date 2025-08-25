# ERP_CORE/production/ai.py
from apps.ai_decision.models import AIDecisionAlert
from .models import ProductionOrder

def detect_delayed_orders():
    from django.utils.timezone import now
    for order in ProductionOrder.objects.all():
        if order.deadline and order.deadline < now().date() and order.status != 'Completed':
            AIDecisionAlert.objects.create(
                section='production',
                alert_type='تأخير في أمر إنتاج',
                level='high',
                message=f"تأخر في أمر التشغيل {order.order_number} عن موعده."
            )