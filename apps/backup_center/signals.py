# apps/backup_center/signals.py
from __future__ import annotations

import logging
from contextlib import suppress
from typing import Any

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.whatsapp_bot.utils import send_whatsapp_message  # يفترض وجود التطبيق

from .models import BackupRecord

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BackupRecord)
def notify_backup_status(
    sender: type[BackupRecord], instance: BackupRecord, created: bool, **kwargs: Any
) -> None:
    """إرسال إشعارات عند إنشاء نسخة احتياطية جديدة."""
    if not created:
        return

    subject = f"✅ Backup Completed: {instance.file_type}"
    message = (
        "A new backup was created.\n"
        f"Time: {instance.created_at}\n"
        f"File: {instance.file_path}"
    )
    recipients = [getattr(settings, "ADMIN_EMAIL", None)]
    recipients = [r for r in recipients if r]  # إزالة None إن وجد

    if recipients:
        with suppress(Exception):
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)

    # إخطار واتساب (تخضع لوجود التكامل)
    with suppress(Exception):
        phone = getattr(settings, "WHATSAPP_TO", None) or "admin"
        wa_message = "\n".join(
            [
                "✅ [ERP Backup]",
                f"Type: {instance.file_type}",
                f"Time: {instance.created_at}",
            ]
        )
        # توقيع الدالة: send_whatsapp_message(phone: str, message: str) -> None
        send_whatsapp_message(phone, wa_message)
