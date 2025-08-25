from django.shortcuts import render, redirect, get_object_or_404
from .models import Campaign, CampaignTarget
from .forms import CampaignForm
from apps.clients.models import Client
from django.contrib import messages
from django.core.mail import send_mail  # لبريد إلكتروني

# ========================
# حملات وعرض
# ========================
def campaign_list(request):
    campaigns = Campaign.objects.all().order_by('-scheduled_date')
    return render(request, 'campaigns/campaign_list.html', {'campaigns': campaigns})

def create_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.created_by = request.user.employee
            campaign.save()

            # استهداف جميع العملاء مؤقتاً
            for client in Client.objects.all():
                CampaignTarget.objects.create(campaign=campaign, client=client)

            messages.success(request, "تم إنشاء الحملة بنجاح.")
            return redirect('campaigns:campaign_list')
    else:
        form = CampaignForm()
    return render(request, 'campaigns/campaign_form.html', {'form': form})

def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    targets = campaign.targets.all()
    return render(request, 'campaigns/campaign_detail.html', {'campaign': campaign, 'targets': targets})

# ========================
# إرسال الحملة (Flow)
# ========================
def send_campaign(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if campaign.is_sent:
        messages.warning(request, "تم إرسال هذه الحملة مسبقًا.")
        return redirect('campaigns:campaign_detail', pk=pk)

    for target in campaign.targets.all():
        client = target.client
        if campaign.channel == 'email':
            send_mail(
                subject=campaign.name,
                message=campaign.content,
                from_email='noreply@erp.local',
                recipient_list=[client.email],
                fail_silently=True,
            )
            target.is_delivered = True
            target.save()
        elif campaign.channel == 'sms':
            # placeholder لدمج مزود SMS حقيقي
            print(f"🔔 إرسال SMS إلى {client.phone}: {campaign.content}")
            target.is_delivered = True
            target.save()
        elif campaign.channel == 'whatsapp':
            # placeholder لتكامل واتساب
            print(f"💬 إرسال WhatsApp إلى {client.phone}: {campaign.content}")
            target.is_delivered = True
            target.save()

    campaign.is_sent = True
    campaign.save()
    messages.success(request, "✅ تم إرسال الحملة بنجاح.")
    return redirect('campaigns:campaign_detail', pk=pk)

# ========================
# صفحات ثانوية
# ========================
def index(request):
    return render(request, 'campaigns/index.html')

def app_home(request):
    return render(request, 'apps/campaigns/home.html', {'app': 'campaigns'})
