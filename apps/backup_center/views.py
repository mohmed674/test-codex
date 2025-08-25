from django.shortcuts import render
from .models import BackupRecord
from .tasks import create_database_backup, create_media_backup
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def backup_dashboard(request):
    if request.method == "POST":
        if 'db_backup' in request.POST:
            create_database_backup()
        elif 'media_backup' in request.POST:
            create_media_backup()
    records = BackupRecord.objects.order_by('-created_at')
    return render(request, 'backup_center/dashboard.html', {'records': records})


from django.shortcuts import render

def index(request):
    return render(request, 'backup_center/index.html')


def app_home(request):
    return render(request, 'apps/backup_center/home.html', {'app': 'backup_center'})
