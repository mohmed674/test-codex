# apps/campaigns/tasks.py
from __future__ import annotations

import logging
from typing import Iterable

from celery import shared_task
from django.utils import timezone

from .models import Campaign
from .reports import _campaign_targets  # reuse robust target resolver

logger = logging.getLogger(__name__)


@shared_task
def send_scheduled_campaigns() -> None:
    """
    Mark scheduled campaigns as sent and update their targets as delivered.

    This task is schema-resilient:
    - It does not assume the related name for targets; uses `_campaign_targets`.
    - It checks existence of fields before setting them (is_delivered/response).
    """
    campaigns: Iterable[Campaign] = Campaign.objects.filter(
        is_sent=False, scheduled_date__lte=timezone.now()
    )

    for campaign in campaigns:
        targets_qs = _campaign_targets(campaign)
        if targets_qs is None:
            logger.info(
                "No targets relation found for campaign id=%s; marking as sent only.",
                campaign.pk,
            )
            campaign.is_sent = True  # type: ignore[attr-defined]
            campaign.save(update_fields=["is_sent"])
            continue

        updated = 0
        for target in targets_qs:
            # محاكاة إرسال الرسالة: اضبط الحقول إن وُجدت
            if hasattr(target, "is_delivered"):
                setattr(target, "is_delivered", True)
            if hasattr(target, "response"):
                setattr(target, "response", "تم الإرسال")
            target.save()
            updated += 1

        if hasattr(campaign, "is_sent"):
            campaign.is_sent = True  # type: ignore[attr-defined]
            campaign.save(update_fields=["is_sent"])
        else:
            campaign.save()

        logger.info(
            "Campaign id=%s processed; targets updated=%d", campaign.pk, updated
        )
