# apps/campaigns/views.py
from __future__ import annotations

from typing import Iterable

from django.contrib import messages
from django.core.mail import send_mail  # لبريد إلكتروني
from django.shortcuts import get_object_or_404, redirect, render

from apps.clients.models import Client

from .forms import CampaignForm
from .models import Campaign, CampaignTarget
from .reports import _campaign_targets  # حلّ مرن للوصول إلى أهداف الحملة


# ========================
# حملات وعرض
# ========================
def campaign_list(request):
    campaigns = Campaign.objects.all().order_by("-scheduled_date")
    return render(request, "campaigns/campaign_list.html", {"campaigns": campaigns})


def create_campaign(request):
    if request.method == "POST":
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            # احذر من غياب العلاقة employee في بعض المشاريع
            if hasattr(request.user, "employee"):
                campaign.created_by = request.user.employee  # type: ignore[attr-defined]
            campaign.save()

            # استهداف جميع العملاء مؤقتاً
            for client in Client.objects.all():
                CampaignTarget.objects.create(campaign=campaign, client=client)

            messages.success(request, "تم إنشاء الحملة بنجاح.")
            return redirect("campaigns:campaign_list")
    else:
        form = CampaignForm()
    return render(request, "campaigns/campaign_form.html", {"form": form})


def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    targets_qs = _campaign_targets(campaign)
    targets = list(targets_qs) if targets_qs is not None else []
    return render(
        request,
        "campaigns/campaign_detail.html",
        {"campaign": campaign, "targets": targets},
    )


# ========================
# إرسال الحملة (Flow)
# ========================
def send_campaign(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if getattr(campaign, "is_sent", False):
        messages.warning(request, "تم إرسال هذه الحملة مسبقًا.")
        return redirect("campaigns:campaign_detail", pk=pk)

    targets_qs = _campaign_targets(campaign)
    targets: Iterable[CampaignTarget] = targets_qs or []

    for target in targets:
        client = getattr(target, "client", None)

        if (
            getattr(campaign, "channel", "") == "email"
            and client
            and getattr(client, "email", "")
        ):
            send_mail(
                subject=getattr(campaign, "name", ""),
                message=getattr(campaign, "content", ""),
                from_email="noreply@erp.local",
                recipient_list=[client.email],
                fail_silently=True,
            )
            if hasattr(target, "is_delivered"):
                target.is_delivered = True  # type: ignore[attr-defined]
            target.save()

        elif (
            getattr(campaign, "channel", "") == "sms"
            and client
            and getattr(client, "phone", "")
        ):
            # placeholder لدمج مزود SMS حقيقي
            print(
                f"🔔 إرسال SMS إلى {client.phone}: {getattr(campaign, 'content', '')}"
            )
            if hasattr(target, "is_delivered"):
                target.is_delivered = True  # type: ignore[attr-defined]
            target.save()

        elif (
            getattr(campaign, "channel", "") == "whatsapp"
            and client
            and getattr(client, "phone", "")
        ):
            # placeholder لتكامل واتساب
            print(
                f"💬 إرسال WhatsApp إلى {client.phone}: {getattr(campaign, 'content', '')}"
            )
            if hasattr(target, "is_delivered"):
                target.is_delivered = True  # type: ignore[attr-defined]
            target.save()

    if hasattr(campaign, "is_sent"):
        campaign.is_sent = True  # type: ignore[attr-defined]
        campaign.save(update_fields=["is_sent"])
    else:
        campaign.save()

    messages.success(request, "✅ تم إرسال الحملة بنجاح.")
    return redirect("campaigns:campaign_detail", pk=pk)


# ========================
# صفحات ثانوية
# ========================
def index(request):
    return render(request, "campaigns/index.html")


def app_home(request):
    return render(request, "apps/campaigns/home.html", {"app": "campaigns"})
