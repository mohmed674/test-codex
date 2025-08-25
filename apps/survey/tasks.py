from django.utils import timezone
from .models import SurveyResponse
from datetime import timedelta

def archive_old_surveys():
    """
    مهمة أرشفة الردود القديمة على الاستبيانات بعد مرور 6 أشهر.
    """
    threshold = timezone.now() - timedelta(days=180)
    old_responses = SurveyResponse.objects.filter(submitted_at__lt=threshold)
    archived_count = old_responses.count()
    old_responses.delete()
    return f"تم حذف {archived_count} من الردود القديمة."
