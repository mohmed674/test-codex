# ERP_CORE/internal_monitoring/security.py

from django.utils import timezone
from django.contrib.auth.models import User

def suspend_user_temporarily(user, duration_minutes=30):
    user.is_active = False
    user.profile.suspension_end = timezone.now() + timezone.timedelta(minutes=duration_minutes)
    user.save()
