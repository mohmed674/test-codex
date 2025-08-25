# -*- coding: utf-8 -*-
import os, sys, re, json, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.append(str(BASE))

# ---------- helpers ----------
def read(p): return p.read_text(encoding="utf-8") if p.exists() else ""
def write(p, s): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(s, encoding="utf-8")
def ensure_line_in_list(src, list_name, line_to_add):
    # يضيف سطر داخل قائمة urlpatterns = [ ... ]
    m = re.search(rf"{list_name}\s*=\s*\[(.*?)\]", src, flags=re.S)
    if m:
        inside = m.group(1)
        if line_to_add.strip() not in inside:
            new_inside = (inside + ("\n" if inside.strip() else "") + line_to_add).rstrip()
            start, end = m.span(1)
            return src[:start] + new_inside + src[end:]
        return src
    else:
        return src + f"\n{list_name} = [\n{line_to_add}\n]\n"

# ---------- 0) inventory/state ----------
INV = BASE / "project_inventory.json"
STATE = BASE / "project_state.json"
inv = json.loads(read(INV)) if INV.exists() else {}
apps_info = inv.get("apps", {})
missing_admin = inv.get("missing_admin", [])

# ---------- 1) settings sanity (STATIC/MEDIA/Templates dirs) ----------
(core_tpl_dir := BASE / "core" / "templates" / "core").mkdir(parents=True, exist_ok=True)
(BASE / "static").mkdir(exist_ok=True)
(BASE / "media").mkdir(exist_ok=True)
base_core_html = core_tpl_dir / "base.html"
if not base_core_html.exists():
    write(base_core_html, """<!DOCTYPE html><html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{% block title %}ERP{% endblock %}</title>
<link rel="stylesheet" href="/static/css/erp.css">
</head><body>{% block content %}{% endblock %}</body></html>""")

# ---------- 2) admin fixes for core missing ----------
if missing_admin:
    core_admin = BASE / "core" / "admin.py"
    admin_src = read(core_admin)
    # تأكد من import
    if "from django.contrib import admin" not in admin_src:
        admin_src = "from django.contrib import admin\n" + admin_src
    if "from core.models" not in admin_src:
        # اجمع الموديلات المفقودة من core فقط
        core_miss = [m.split(".")[1] for m in missing_admin if m.startswith("core.")]
        if core_miss:
            admin_src = f"from core.models import {', '.join(sorted(set(core_miss)))}\n" + admin_src
            for M in sorted(set(core_miss)):
                if re.search(rf"@admin\.register\({M}\)|admin\.site\.register\({M}\)", admin_src) is None:
                    admin_src += f"\ntry:\n    admin.site.register({M})\nexcept admin.sites.AlreadyRegistered:\n    pass\n"
            write(core_admin, admin_src)

# ---------- 3) Inventory proxy alias ----------
inv_models = apps_info.get("inventory", {}).get("models", [])
if "Inventory" not in inv_models:
    inventory_models = BASE / "apps" / "inventory" / "models.py"
    src = read(inventory_models)
    if "class Inventory(" not in src:
        # ابحث عن تعريف InventoryItem
        if "class InventoryItem(" in src:
            src += """

# ---- AUTO PROXY ALIAS (generated) ----
try:
    class Inventory(InventoryItem):  # proxy alias to satisfy imports
        class Meta:
            proxy = True
            verbose_name = "Inventory"
            verbose_name_plural = "Inventory"
except NameError:
    pass
# ---- END AUTO PROXY ----
"""
            write(inventory_models, src)

# ---------- 4) normalize suppliers urls (حزمة ثابتة + API مستقر) ----------
sup_urls_pkg = BASE / "apps" / "suppliers" / "urls"
sup_urls_pkg.mkdir(parents=True, exist_ok=True)
# main.py
main_py = sup_urls_pkg / "main.py"
main_src = read(main_py)
if "urlpatterns" not in main_src:
    main_src = "from django.urls import path, include\nurlpatterns = [path('api/', include('apps.suppliers.urls.api'))]\n"
else:
    if "apps.suppliers.urls.api" not in main_src:
        main_src = ensure_line_in_list(main_src, "urlpatterns", "    path('api/', include('apps.suppliers.urls.api')),")
write(main_py, main_src)
# __init__.py يصدر urlpatterns من main
write(sup_urls_pkg / "__init__.py", "from .main import urlpatterns\n")
# api.py resilient
api_py = sup_urls_pkg / "api.py"
if not api_py.exists():
    write(api_py, """from django.urls import path
from django.http import JsonResponse
try:
    from apps.suppliers import api_views as _api
    HAVE = True
except Exception:
    HAVE = False

def _list(_): return JsonResponse({"ok": True, "endpoint": "suppliers/api/list", "using": "fallback"})
def _detail(_, pk:int): return JsonResponse({"ok": True, "endpoint": f"suppliers/api/detail/{pk}", "using": "fallback"})

urlpatterns = []
urlpatterns.append(path("list/", (_api.SupplierListAPIView.as_view() if HAVE and hasattr(_api, "SupplierListAPIView") else _list), name="supplier_list_api"))
urlpatterns.append(path("detail/<int:pk>/", (_api.SupplierDetailAPIView.as_view() if HAVE and hasattr(_api, "SupplierDetailAPIView") else _detail), name="supplier_detail_api"))
""")

# ---------- 5) wire config/urls.py لكل التطبيقات تلقائيًا ----------
config_urls = BASE / "config" / "urls.py"
cfg = read(config_urls)
if "from django.urls import path, include" not in cfg:
    cfg = "from django.urls import path, include\n" + cfg
if "from django.contrib import admin" not in cfg:
    cfg = "from django.contrib import admin\n" + cfg
if "urlpatterns" not in cfg:
    cfg += "\nurlpatterns = [path('admin/', admin.site.urls)]\n"

# core في الجذر
cfg = ensure_line_in_list(cfg, "urlpatterns", "    path('', include('core.urls')),")

# apps/* التي تملك urls.py
apps_root = BASE / "apps"
if apps_root.exists():
    for app_dir in sorted([p for p in apps_root.iterdir() if p.is_dir()]):
        # حالات خاصة للموردين → استخدم الحزمة
        if app_dir.name == "suppliers":
            cfg = ensure_line_in_list(cfg, "urlpatterns", "    path('suppliers/', include('apps.suppliers.urls')),")
            continue
        # urls.py
        if (app_dir / "urls.py").exists():
            cfg = ensure_line_in_list(cfg, "urlpatterns", f"    path('{app_dir.name}/', include('apps.{app_dir.name}.urls')),")

write(config_urls, cfg)

# ---------- 6) project_state update ----------
st = {"last_script": "erp_autofix_all.py", "status": "autofixed", "last_updated": datetime.datetime.utcnow().isoformat()}
try:
    prev = json.loads(read(STATE)) if STATE.exists() else {}
    prev.update(st)
    st = prev
except: pass
write(STATE, json.dumps(st, indent=2, ensure_ascii=False))

print("✅ ERP autofix completed: admin/core, inventory proxy, suppliers urls/api, config urls wiring, core/templates/base.html")
