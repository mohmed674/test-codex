from .models import RiskIncident

def monitoring_data(request):
    return {
        'monitoring_data': {
            'discrepancies_count': RiskIncident.objects.filter(status='unresolved').count()
        }
    }
