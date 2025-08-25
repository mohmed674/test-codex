from django.db import models
from django.utils.translation import gettext_lazy as _

class BackupRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    file_path = models.CharField(max_length=500, verbose_name=_("Backup File Path"))
    file_type = models.CharField(max_length=50, choices=[("database", _("Database")), ("media", _("Media Files"))])
    
    class Meta:
        verbose_name = _("Backup Record")
        verbose_name_plural = _("Backup Records")

    def __str__(self):
        return f"{self.file_type} - {self.created_at}"
