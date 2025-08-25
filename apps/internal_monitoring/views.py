# ERP_CORE/internal_monitoring/views.py

from django.shortcuts import render
from .models import RiskIncident
from django.db.models import Count

def risk_dashboard_view(request):
    incidents = RiskIncident.objects.all().order_by('-created_at')[:100]

    stats = RiskIncident.objects.values('risk_level').annotate(count=Count('id'))
    by_category = RiskIncident.objects.values('category').annotate(count=Count('id'))

    return render(request, 'internal_monitoring/risk_dashboard.html', {
        'incidents': incidents,
        'stats': stats,
        'by_category': by_category,
    })


from django.shortcuts import render

def index(request):
    return render(request, 'internal_monitoring/index.html')


def app_home(request):
    return render(request, 'apps/internal_monitoring/home.html', {'app': 'internal_monitoring'})
