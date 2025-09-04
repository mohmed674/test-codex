# core/management/commands/generate_stub_templates.py
# -*- coding: utf-8 -*-
"""
Generate placeholder home.html templates for each app under templates/apps/<app>/home.html,
plus a set of extra templates discovered from logs. Non-destructive: creates files only if missing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, List, Tuple

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

EXTRA_FILES: List[Tuple[str, str]] = [
    ("apps/crm/home.html", "crm"),
    ("dark_mode/overview.html", "dark_mode"),
    ("employees/employee_list.html", "employees"),
    ("site/home.html", "site"),
]

TEMPLATE_HTML = """<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8"/>
  <title>{title} | ERP</title>
  <style>
    body{{font-family:Segoe UI, Tahoma, sans-serif;background:#0f172a;color:#e5e7eb;margin:0;padding:40px}}
    .card{{max-width:760px;margin:auto;background:#111827;border:1px solid #1f2937;border-radius:12px;padding:24px}}
    h1{{margin:0 0 8px;font-size:22px}}
    p,code{{font-size:14px}}
    a{{color:#93c5fd;text-decoration:none}}
  </style>
</head>
<body>
  <div class="card">
    <h1>واجهة مؤقتة: {title}</h1>
    <p>صفحة افتراضية للتجربة السريعة. عدّل القالب لاحقًا.</p>
    <p><a href="/">الرئيسية</a></p>
  </div>
</body>
</html>
"""


class Command(BaseCommand):
    help = _(
        "توليد قوالب home.html لكل التطبيقات تحت templates/apps/<app>/home.html + قوالب إضافية."
    )

    def handle(self, *args: str, **opts: Any) -> None:
        """
        Create missing stub templates under BASE_DIR/templates. Does not overwrite existing files.
        """
        base = Path(settings.BASE_DIR)
        tpl_root = base / "templates"
        apps_dir = base / "apps"

        created: List[str] = []

        # 1) لكل التطبيقات اعمل apps/<app>/home.html
        if apps_dir.exists():
            for p in sorted(apps_dir.iterdir(), key=lambda x: x.name.lower()):
                if not p.is_dir():
                    continue
                app = p.name
                if app.startswith("__"):
                    continue
                target = tpl_root / "apps" / app / "home.html"
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_text(TEMPLATE_HTML.format(title=app), encoding="utf-8")
                    created.append(str(target.relative_to(base)))

        # 2) قوالب إضافية مطلوبة من اللوج
        for rel, title in EXTRA_FILES:
            target = tpl_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text(TEMPLATE_HTML.format(title=title), encoding="utf-8")
                created.append(str(target.relative_to(base)))

        if created:
            self.stdout.write(self.style.SUCCESS(_("✅ تم إنشاء القوالب:")))
            for p in created:
                self.stdout.write(f" - {p}")
        else:
            self.stdout.write(self.style.WARNING(_("ℹ️ لا قوالب جديدة مطلوبة.")))
