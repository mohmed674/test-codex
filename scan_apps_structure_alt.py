# -*- coding: utf-8 -*-
import os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APPS_DIR = ROOT / "apps"
FILES = ["models.py", "views.py", "urls.py", "forms.py", "admin.py"]

def has_index_view(app_path: Path) -> bool:
    views = app_path / "views.py"
    urls = app_path / "urls.py"
    pat_func = re.compile(r"def\s+index\s*\(", re.IGNORECASE)
    pat_cbv  = re.compile(r"class\s+Index[A-Za-z0-9_]*\(", re.IGNORECASE)
    try:
        if views.exists() and pat_func.search(views.read_text(encoding="utf-8", errors="ignore")):
            return True
    except: pass
    try:
        if urls.exists() and re.search(r"\bindex\b", urls.read_text(encoding="utf-8", errors="ignore"), re.IGNORECASE):
            return True
    except: pass
    return False

def has_templates_for(app_name: str, app_path: Path) -> bool:
    a = app_path / "templates" / app_name
    b = app_path / "templates"
    if a.is_dir(): return True
    if b.is_dir():
        for _, _, fs in os.walk(b):
            if any(f.lower().endswith((".html",".htm")) for f in fs):
                return True
    return False

def is_app_dir(d: Path) -> bool:
    return d.is_dir() and not d.name.startswith("__")

def line(label, ok): return f"   - {label:<12} {'✅' if ok else '❌'}"

def main():
    if not APPS_DIR.is_dir():
        print(f"❌ لا يوجد مجلد apps في: {ROOT}")
        return
    apps = sorted([p for p in APPS_DIR.iterdir() if is_app_dir(p)], key=lambda p: p.name.lower())
    print(f"\n🔍 فحص التطبيقات داخل: {APPS_DIR.name}\n")
    total, complete = 0, 0
    for app_path in apps:
        total += 1
        app = app_path.name
        print(f"📦 [{app}]")
        status = {fn: (app_path / fn).exists() for fn in FILES}
        for fn, ok in status.items():
            print(line(fn, ok))
        tmpl_ok = has_templates_for(app, app_path)
        print(f"   - templates/{app}/ {'✅' if tmpl_ok else '❌'}")
        idx_ok = has_index_view(app_path)
        print(f"     ↪️ index {'✅' if idx_ok else '❌'}\n")
        if all(status.values()) and tmpl_ok: complete += 1
    print("============================================================")
    print("📊 ملخص")
    print("============================================================")
    print(f"إجمالي التطبيقات: {total}")
    print(f"تطبيقات مكتملة (ملفات أساسية + قوالب): {complete}/{total}")
    print("============================================================")

if __name__ == "__main__":
    main()
