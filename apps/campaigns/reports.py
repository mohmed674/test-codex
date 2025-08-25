from .models import Campaign, CampaignTarget

def get_campaign_summary(campaign_id):
    try:
        campaign = Campaign.objects.get(pk=campaign_id)
        total_targets = campaign.targets.count()
        delivered = campaign.targets.filter(is_delivered=True).count()
        responded = campaign.targets.exclude(response__isnull=True).exclude(response__exact="").count()

        delivery_rate = (delivered / total_targets * 100) if total_targets else 0
        response_rate = (responded / total_targets * 100) if total_targets else 0

        return {
            'campaign': campaign.name,
            'channel': campaign.channel,
            'scheduled': campaign.scheduled_date,
            'is_sent': campaign.is_sent,
            'total_targets': total_targets,
            'delivered': delivered,
            'responded': responded,
            'delivery_rate': round(delivery_rate, 2),
            'response_rate': round(response_rate, 2),
        }
    except Campaign.DoesNotExist:
        return None
