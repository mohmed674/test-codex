# tools/quick_expose_apps.py
import os, re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # D:\ERP_CORE
APPS = BASE / "apps"
TEMPLATES_ROOT = BASE / "templates" / "apps"
CONFIG_URLS = BASE / "config" / "urls.py"

SKIP = {"__pycache__", "__init__.py"}

def ensure_templates_root():
    TEMPLATES_ROOT.mkdir(parents=True, exist_ok=True)

def snake_to_title(s):
    return re.sub(r"_+", " ", s).title()

def ensure_app_scaffold(app_dir: Path):
    app = app_dir.name
    if app in SKIP: return False

    urls_py = app_dir / "urls.py"
    views_py = app_dir / "views.py"
    tmpl_dir = TEMPLATES_ROOT / app
    tmpl_dir.mkdir(parents=True, exist_ok=True)
    home_html = tmpl_dir / "home.html"

    created_any = False

    # views.py -> app_home
    if not views_py.exists():
        views_py.write_text(f"""from django.http import HttpResponse
from django.shortcuts import render

def app_home(request):
    return render(request, 'apps/{app}/home.html', {{'app': '{app}'}})
""", encoding="utf-8")
        created_any = True
    else:
        s = views_py.read_text(encoding="utf-8")
        if "def app_home(" not in s:
            s += f"""

def app_home(request):
    return render(request, 'apps/{app}/home.html', {{'app': '{app}'}})
"""
            views_py.write_text(s, encoding="utf-8")
            created_any = True

    # urls.py -> app_name + '' route
    if not urls_py.exists():
        urls_py.write_text(f"""from django.urls import path
from . import views

app_name = '{app}'

urlpatterns = [
    path('', views.app_home, name='home'),
]
""", encoding="utf-8")
        created_any = True
    else:
        s = urls_py.read_text(encoding="utf-8")
        if "app_name" not in s:
            s = f"app_name = '{app}'\n" + s
        if "path(''," not in s:
            s = s.rstrip() + "\n\nfrom . import views\nurlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [\n    path('', views.app_home, name='home'),\n]\n"
        urls_py.write_text(s, encoding="utf-8")
        created_any = True

    # template
    if not home_html.exists():
        home_html.write_text(f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8"/>
  <title>{snake_to_title(app)} | ERP</title>
  <style>
    body{{font-family:Segoe UI, Tahoma, sans-serif;background:#0f172a;color:#e2e8f0;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}}
    .card{{background:#111827;border:1px solid #1f2937;border-radius:14px;padding:28px;min-width:360px;box-shadow:0 10px 30px rgba(0,0,0,.35)}}
    h1{{margin:0 0 10px;font-size:22px}}
    .tag{{display:inline-block;background:#1f2937;color:#93c5fd;border:1px solid #374151;border-radius:999px;padding:4px 10px;font-size:12px}}
    a{{color:#93c5fd;text-decoration:none}}
  </style>
</head>
<body>
  <div class="card">
    <span class="tag">/apps/{app}</span>
    <h1>وِجهة {snake_to_title(app)}</h1>
    <p>تم إنشاء صفحة افتراضية بنجاح. عدّلها لاحقًا من <code>templates/apps/{app}/home.html</code>.</p>
    <p><a href="/">الذهاب للواجهة الرئيسية</a></p>
  </div>
</body>
</html>
""", encoding="utf-8")
        created_any = True

    return created_any

def main():
    ensure_templates_root()

    if not APPS.exists():
        print("❌ apps/ غير موجود")
        return

    changed = []
    for app_dir in sorted(p for p in APPS.iterdir() if p.is_dir()):
        if app_dir.name in SKIP: continue
        if ensure_app_scaffold(app_dir):
            changed.append(app_dir.name)

    # تأكد أن config/urls.py به include عام (إنت بالفعل ربطت المسارات سابقًا)
    # لن نعدل عليه هنا لتفادي تضارب، هذا سكربت تعريضي فقط.

    print("✅ تم تجهيز صفحات افتراضية للتطبيقات التالية:")
    for a in changed:
        print(" -", a)
    if not changed:
        print("ℹ️ لا تغييرات مطلوبة. كل التطبيقات مكشوفة بالفعل.")

if __name__ == "__main__":
    main()
