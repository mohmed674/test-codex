# ERP_CORE/purchases/tasks.py

from celery import shared_task
from django.utils.timezone import now
from .models import PurchaseRequest
from apps.notifications.utils import notify_user_group

@shared_task
def remind_pending_purchase_requests():
    """
    تذكير دوري للطلبات غير المعالجة
    """
    pending = PurchaseRequest.objects.filter(status='pending')
    for req in pending:
        notify_user_group(
            group_name='Purchase Managers',
            message=f"⏰ طلب شراء معلق من قسم {req.department.name} منذ {req.created_at.date()}."
        )
