# -*- coding: utf-8 -*-
# QMS AppConfig — Quality Management System (AQL / SPC / CAPA)

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class QmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'apps.qms'
    verbose_name = _("إدارة الجودة (QMS) — AQL / SPC / CAPA")

    def ready(self):
        # ملاحظة: إشارات ما قبل الحفظ مُعرّفة داخل models.py (لا حاجة لاستيراد إضافي هنا)
        # ضع هنا أي نقاط ربط مستقبلية (listeners) أو تكاملات.
        pass
