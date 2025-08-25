# tools/force_make_templates.py
# -*- coding: utf-8 -*-
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TPL = BASE / "templates"

APPS = [
    "api_gateway","attendance","crm","departments","discipline",
    "employee_monitoring","internal_monitoring","maintenance","monitoring",
    "pattern","payroll","pos","sales","survey","tracking",
    "voice_commands","whatsapp_bot",
]

EXTRA = {
    "dark_mode/overview.html": "dark_mode",
    "employees/employee_list.html": "employees",
}

HTML = """<!doctype html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"/><title>{title} | ERP</title>
<style>body{{font-family:Segoe UI,Tahoma,sans-serif;background:#0f172a;color:#e5e7eb;margin:0;padding:40px}}
.card{{max-width:760px;margin:auto;background:#111827;border:1px solid #1f2937;border-radius:12px;padding:24px}}
a{{color:#93c5fd;text-decoration:none}}</style></head>
<body><div class="card"><h1>واجهة مؤقتة: {title}</h1><p>صفحة مؤقتة للتجربة.</p><p><a href="/">الرئيسية</a></p></div></body></html>
"""

# اكتب/استبدل apps/<app>/home.html
created = []
for app in APPS:
    target = TPL / "apps" / app / "home.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(HTML.format(title=app), encoding="utf-8")
    created.append(str(target.relative_to(BASE)))

# اكتب/استبدل ملفات إضافية
for rel, title in EXTRA.items():
    target = TPL / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(HTML.format(title=title), encoding="utf-8")
    created.append(str(target.relative_to(BASE)))

print("✅ Forced templates written:")
for c in created:
    print(" -", c)
