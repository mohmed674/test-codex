from celery import shared_task
from .models import POSOrder
from django.utils import timezone

@shared_task
def auto_close_old_sessions():
    from .models import POSSession
    sessions = POSSession.objects.filter(is_closed=False, start_time__lt=timezone.now()-timezone.timedelta(hours=8))
    for session in sessions:
        session.end_time = timezone.now()
        session.is_closed = True
        session.save()
