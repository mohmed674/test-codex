from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from jsonfield import JSONField  # استيراد مباشر وصحيح

User = get_user_model()


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        INFO = 'info', _('معلومات')
        WARNING = 'warning', _('تحذير')
        CRITICAL = 'critical', _('هام')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_("المستخدم"),
    )
    title = models.CharField(max_length=255, verbose_name=_("عنوان الإشعار"))
    message = models.TextField(verbose_name=_("نص الإشعار"))
    notification_type = models.CharField(
        max_length=10,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
        verbose_name=_("نوع الإشعار"),
    )
    link = models.URLField(blank=True, null=True, verbose_name=_("رابط"))

    # ✅ الحقل بدون تحذير محرر الأكواد
    metadata = JSONField(blank=True, null=True, verbose_name=_("بيانات إضافية"))

    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("تاريخ الإنشاء"))
    read_at = models.DateTimeField(blank=True, null=True, verbose_name=_("تاريخ القراءة"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))

    class Meta:
        verbose_name = _("إشعار")
        verbose_name_plural = _("الإشعارات")
        ordering = ['-created_at']

    def mark_as_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])

    @property
    def is_read(self):
        return self.read_at is not None

    def __str__(self):
        return f"{self.title} - للمستخدم {self.user} بتاريخ {self.created_at.strftime('%Y-%m-%d %H:%M')}"
