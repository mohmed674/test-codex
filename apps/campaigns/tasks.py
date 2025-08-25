from celery import shared_task
from .models import Campaign, CampaignTarget
from django.utils import timezone

@shared_task
def send_scheduled_campaigns():
    campaigns = Campaign.objects.filter(is_sent=False, scheduled_date__lte=timezone.now())
    for campaign in campaigns:
        for target in campaign.targets.all():
            # محاكاة إرسال الرسالة
            target.is_delivered = True
            target.response = "تم الإرسال"
            target.save()
        campaign.is_sent = True
        campaign.save()
