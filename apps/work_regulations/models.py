from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Regulation(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Regulation Title"))
    content_html = models.TextField(verbose_name=_("HTML Content"))
    pdf_file = models.FileField(upload_to='regulations/', null=True, blank=True, verbose_name=_("PDF File"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Work Regulation")
        verbose_name_plural = _("Work Regulations")

    def __str__(self):
        return self.title


class EmployeeAgreement(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Employee"))
    regulation = models.ForeignKey(Regulation, on_delete=models.CASCADE, verbose_name=_("Regulation"))
    agreed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Agreement")
        verbose_name_plural = _("Agreements")
        unique_together = ('employee', 'regulation')

    def __str__(self):
        return f"{self.employee} - {self.regulation}"
