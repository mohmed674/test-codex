# core/management/commands/debug_templates.py
# -*- coding: utf-8 -*-
"""
Verify that specified templates are discoverable by Django's template loader and show search paths.
Non-destructive diagnostic command.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Tuple

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

TARGETS: List[str] = [
    # اللي لسه بترمي TemplateDoesNotExist
    "apps/api_gateway/home.html",
    "apps/attendance/home.html",
    "apps/crm/home.html",
    "apps/departments/home.html",
    "apps/discipline/home.html",
    "apps/employee_monitoring/home.html",
    "apps/internal_monitoring/home.html",
    "apps/maintenance/home.html",
    "apps/monitoring/home.html",
    "apps/pattern/home.html",
    "apps/payroll/home.html",
    "apps/pos/home.html",
    "apps/sales/home.html",
    "apps/survey/home.html",
    "apps/tracking/home.html",
    "apps/voice_commands/home.html",
    "apps/whatsapp_bot/home.html",
    "dark_mode/overview.html",
    "employees/employee_list.html",
]


class Command(BaseCommand):
    help = _("يتحقق هل القوالب موجودة فعليًا في لودر Django ويطبع مسارات البحث.")

    def handle(self, *args: str, **opts: Any) -> None:
        self.stdout.write(_("📂 TEMPLATE DIRS:"))
        try:
            dirs = settings.TEMPLATES[0]["DIRS"]
        except (AttributeError, IndexError, KeyError, TypeError) as e:
            self.stdout.write(self.style.ERROR(f"⚠️ تعذّر قراءة الإعدادات: {e}"))
            return

        for d in dirs:
            self.stdout.write(f" - {Path(d)}")

        missing: List[Tuple[str, str]] = []
        ok: List[str] = []

        for name in TARGETS:
            try:
                get_template(name)
                ok.append(name)
            except Exception as e:  # We want the exact loader error per template
                missing.append((name, f"{e.__class__.__name__}: {e}"))

        self.stdout.write(_("\n✅ FOUND:"))
        self.stdout.write(", ".join(ok) or _("لا شيء"))

        self.stdout.write(_("\n❌ MISSING:"))
        for name, err in missing:
            self.stdout.write(f" - {name} -> {err}")

        # وجود الملفات فعليًا على القرص
        base = Path(settings.BASE_DIR)
        self.stdout.write(_("\n🧭 Files on disk:"))
        for name in TARGETS:
            p = base / "templates" / name
            self.stdout.write(f" - templates/{name} : {'OK' if p.exists() else 'NO'}")
