# core/management/commands/debug_templates.py
# -*- coding: utf-8 -*-
from pathlib import Path
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.conf import settings

TARGETS = [
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
    help = "يتحقق هل القوالب موجودة فعليًا في لودر Django ويطبع مسارات البحث."

    def handle(self, *args, **opts):
        self.stdout.write("📂 TEMPLATE DIRS:")
        for d in settings.TEMPLATES[0]['DIRS']:
            self.stdout.write(f" - {Path(d)}")

        missing = []
        ok = []

        for name in TARGETS:
            try:
                get_template(name)
                ok.append(name)
            except Exception as e:
                missing.append((name, f"{e.__class__.__name__}: {e}"))

        self.stdout.write("\n✅ FOUND:")
        self.stdout.write(", ".join(ok) or "لا شيء")

        self.stdout.write("\n❌ MISSING:")
        for name, err in missing:
            self.stdout.write(f" - {name} -> {err}")

        # كمان نطبع وجود الملفات فعليًا على القرص
        base = Path(getattr(settings, "BASE_DIR"))
        self.stdout.write("\n🧭 Files on disk:")
        for name in TARGETS:
            p = base / "templates" / name
            self.stdout.write(f" - templates/{name} : {'OK' if p.exists() else 'NO'}")
