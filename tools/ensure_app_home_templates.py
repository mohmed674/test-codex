# tools/ensure_app_home_templates.py
# -*- coding: utf-8 -*-
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
APPS = BASE / "apps"
TPL = BASE / "templates"

HTML = """<!doctype html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"/><title>{title} | ERP</title>
<style>body{{font-family:Segoe UI, Tahoma,sans-serif;background:#0f172a;color:#e5e7eb;margin:0;padding:40px}}
.card{{max-width:760px;margin:auto;background:#111827;border:1px solid #1f2937;border-radius:12px;padding:24px}}
a{{color:#93c5fd;text-decoration:none}}</style></head>
<body><div class="card"><h1>واجهة مؤقتة: {title}</h1><p>صفحة افتراضية للتجربة السريعة.</p><p><a href="/">الرئيسية</a></p></div></body></html>
"""

EXTRA = [
    ("apps/crm/home.html", "crm"),
    ("dark_mode/overview.html", "dark_mode"),
    ("employees/employee_list.html", "employees"),
    ("site/home.html", "site"),
]

def write_if_missing(path: Path, title: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(HTML.format(title=title), encoding="utf-8")
        return True
    return False

created = []

# لكل apps/<app>/home.html
for p in sorted(APPS.iterdir()):
    if not p.is_dir() or p.name.startswith("__"):
        continue
    target = TPL / "apps" / p.name / "home.html"
    if write_if_missing(target, p.name):
        created.append(str(target.relative_to(BASE)))

# القوالب الإضافية
for rel, title in EXTRA:
    target = TPL / rel
    if write_if_missing(target, title):
        created.append(str(target.relative_to(BASE)))

if created:
    print("✅ Created:")
    for c in created:
        print(" -", c)
else:
    print("ℹ️ Nothing to create.")
