# core/management/commands/repair_missing_templates.py
# -*- coding: utf-8 -*-
"""
Create missing placeholder templates for apps that failed smoke tests (TemplateDoesNotExist).
Non-destructive: only creates files if they do not already exist.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

HTML = """<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8" />
  <title>{title} | ERP</title>
  <style>
    body{{font-family:Segoe UI,Tahoma,sans-serif;background:#0f172a;color:#e5e7eb;margin:0;padding:40px}}
    .card{{max-width:760px;margin:auto;background:#111827;border:1px solid #1f2937;border-radius:12px;padding:24px}}
    a{{color:#93c5fd;text-decoration:none}}
  </style>
</head>
<body>
  <div class="card">
    <h1>واجهة مؤقتة: {title}</h1>
    <p>صفحة مؤقتة للتجربة.</p>
    <p><a href="/">الرئيسية</a></p>
  </div>
</body>
</html>
"""

APPS_NEED_HOME: List[str] = [
    # من تقرير smoke الأخير (TemplateDoesNotExist)
    "api_gateway",
    "attendance",
    "crm",
    "departments",
    "discipline",
    "employee_monitoring",
    "internal_monitoring",
    "maintenance",
    "monitoring",
    "pattern",
    "payroll",
    "pos",
    "sales",
    "survey",
    "tracking",
    "voice_commands",
    "whatsapp_bot",
]

EXTRA_FILES: Dict[str, str] = {
    # مسارات خاصة ظهرت في الأخطاء
    "dark_mode/overview.html": "dark_mode",
    "employees/employee_list.html": "employees",
}


class Command(BaseCommand):
    help = _(
        "إنشاء القوالب المفقودة (home.html لكل app المطلوبة + القوالب الخاصة المذكورة)."
    )

    def handle(self, *args: str, **opts: Any) -> None:
        """
        Generate missing templates under BASE_DIR/templates without overwriting existing files.
        """
        base = Path(getattr(settings, "BASE_DIR"))
        tpl = base / "templates"
        created: List[str] = []

        # apps/<app>/home.html
        for app in APPS_NEED_HOME:
            target = tpl / "apps" / app / "home.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text(HTML.format(title=app), encoding="utf-8")
                created.append(str(target.relative_to(base)))

        # extra files
        for rel, title in EXTRA_FILES.items():
            target = tpl / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text(HTML.format(title=title), encoding="utf-8")
                created.append(str(target.relative_to(base)))

        if created:
            self.stdout.write(self.style.SUCCESS(_("✅ Created:")))
            for c in created:
                self.stdout.write(f" - {c}")
        else:
            self.stdout.write(self.style.WARNING(_("ℹ️ لا توجد قوالب ناقصة لإنشائها.")))
