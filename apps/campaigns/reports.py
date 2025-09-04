# apps/campaigns/reports.py
from __future__ import annotations

from typing import Optional

from django.apps import apps
from django.db.models import QuerySet

from .models import Campaign


def _campaign_targets(campaign: Campaign) -> Optional[QuerySet]:
    """
    Resolve the related manager holding campaign targets, regardless of its name.

    Strategy:
      1) Check common related names (targets/recipients/audiences/contacts).
      2) Inspect reverse relations dynamically via _meta.related_objects.
      3) Fallback to a concrete CampaignTarget model if present by discovering the FK.
    Returns a QuerySet or None if not found.
    """
    # 1) Common related names
    for rel_name in ("targets", "recipients", "audiences", "contacts"):
        rel = getattr(campaign, rel_name, None)
        if rel is not None and hasattr(rel, "all"):
            return rel.all()

    # 2) Inspect reverse relations dynamically
    try:
        for rel in campaign._meta.related_objects:  # type: ignore[attr-defined]
            accessor = getattr(rel, "get_accessor_name", None)
            if callable(accessor):
                name = accessor()
                if not isinstance(name, str) or not name:
                    continue
                manager = getattr(campaign, name, None)
                if manager is not None and hasattr(manager, "all"):
                    return manager.all()
    except Exception:
        pass

    # 3) Fallback to a concrete model if it exists
    Target = apps.get_model("campaigns", "CampaignTarget")
    if Target is not None:
        try:
            # Discover the FK field pointing to Campaign
            for f in Target._meta.get_fields():  # type: ignore[attr-defined]
                if getattr(f, "is_relation", False) and getattr(
                    f, "many_to_one", False
                ):
                    if getattr(f, "related_model", None) is Campaign:
                        return Target.objects.filter(**{f.name: campaign})
        except Exception:
            return Target.objects.none()

    return None


def get_campaign_summary(campaign_id: int) -> Optional[dict]:
    """
    Return a summary dict for a campaign (safe across schema variations) or None if not found.
    """
    try:
        campaign = Campaign.objects.get(pk=campaign_id)
        targets_qs = _campaign_targets(campaign)

        if targets_qs is None:
            total_targets = delivered = responded = 0
        else:
            total_targets = targets_qs.count()
            delivered = targets_qs.filter(is_delivered=True).count()
            responded = (
                targets_qs.exclude(response__isnull=True)
                .exclude(response__exact="")
                .count()
            )

        delivery_rate = (delivered / total_targets * 100) if total_targets else 0
        response_rate = (responded / total_targets * 100) if total_targets else 0

        return {
            "campaign": campaign.name,
            "channel": getattr(campaign, "channel", ""),
            "scheduled": getattr(campaign, "scheduled_date", None),
            "is_sent": getattr(campaign, "is_sent", False),
            "total_targets": total_targets,
            "delivered": delivered,
            "responded": responded,
            "delivery_rate": round(delivery_rate, 2),
            "response_rate": round(response_rate, 2),
        }
    except Campaign.DoesNotExist:
        return None
