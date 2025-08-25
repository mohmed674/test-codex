# ERP_CORE/internal_monitoring/tasks.py

from django.utils import timezone
from django.contrib.auth.models import User

def reactivate_suspended_users():
    for user in User.objects.filter(is_active=False):
        if hasattr(user, 'profile') and user.profile.suspension_end and user.profile.suspension_end <= timezone.now():
            user.is_active = True
            user.save()
