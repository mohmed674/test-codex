from django.shortcuts import render
from .models import WhatsAppOrder
from django.db.models import Count
from django.utils.timezone import now, timedelta

def whatsapp_dashboard_view(request):
    today = now().date()
    week_ago = today - timedelta(days=7)

    total_orders = WhatsAppOrder.objects.count()
    new_orders_today = WhatsAppOrder.objects.filter(created_at__date=today).count()
    new_orders_week = WhatsAppOrder.objects.filter(created_at__date__gte=week_ago).count()

    top_clients = WhatsAppOrder.objects.values('customer_phone') \
                   .annotate(total=Count('id')).order_by('-total')[:5]

    return render(request, 'whatsapp_bot/dashboard.html', {
        'total_orders': total_orders,
        'new_orders_today': new_orders_today,
        'new_orders_week': new_orders_week,
        'top_clients': top_clients,
    })


# إذا أردت إضافة صفحة الإعدادات لاحقًا، أضفها هكذا:

def whatsapp_settings_view(request):
    # المنطق المطلوب
    return render(request, 'whatsapp_bot/settings.html')


from django.shortcuts import render

def index(request):
    return render(request, 'whatsapp_bot/index.html')


def app_home(request):
    return render(request, 'apps/whatsapp_bot/home.html', {'app': 'whatsapp_bot'})
