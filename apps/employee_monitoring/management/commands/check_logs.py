from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from apps.employee_monitoring.models import DataLogMonitor
from datetime import timedelta

class Command(BaseCommand):
    help = 'Check who did not enter data today'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        sections = ['production', 'attendance', 'evaluation']
        users = User.objects.all()

        for user in users:
            for section in sections:
                latest = DataLogMonitor.objects.filter(
                    user=user,
                    section=section,
                    last_entry_time__date=today
                ).first()

                if not latest:
                    DataLogMonitor.objects.update_or_create(
                        user=user,
                        section=section,
                        defaults={
                            'last_entry_time': timezone.now(),
                            'entry_status': 'missing',
                            'notes': 'لم يتم تسجيل بيانات اليوم'
                        }
                    )
        self.stdout.write(self.style.SUCCESS('✅ تمت مراجعة السجلات اليومية بنجاح'))
