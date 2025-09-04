# -*- coding: utf-8 -*-
from __future__ import annotations

from django.apps import AppConfig


class QmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.qms"
    verbose_name = "QMS"

    def ready(self) -> None:
        # ضع أي imports للإشارات هنا إن وجدت (بدون تنفيذ جانبي ثقيل)
        # from . import signals  # noqa: F401
        return None
