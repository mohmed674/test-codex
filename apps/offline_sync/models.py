from django.db import models
from django.utils import timezone

class OfflineSyncLog(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    synced_at = models.DateTimeField(default=timezone.now)
    data_summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Sync by {self.user.username} at {self.synced_at.strftime('%Y-%m-%d %H:%M')}"
