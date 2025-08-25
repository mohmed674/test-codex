from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import OfflineSyncLog

@login_required
def dashboard(request):
    logs = OfflineSyncLog.objects.filter(user=request.user).order_by('-synced_at')[:20]
    return render(request, 'offline_sync/dashboard.html', {'logs': logs})


from django.shortcuts import render

def index(request):
    return render(request, 'offline_sync/index.html')


def app_home(request):
    return render(request, 'apps/offline_sync/home.html', {'app': 'offline_sync'})
