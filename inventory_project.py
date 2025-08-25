import os, sys, json, django, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.apps import apps as dj_apps
from django.contrib import admin
from django.urls import get_resolver

def find_local_apps():
    found = {}
    # core بجانب manage.py
    core_dir = BASE_DIR / "core"
    if (core_dir / "apps.py").exists() and (core_dir / "models.py").exists():
        found["core"] = "core"

    # apps/* (كل التطبيقات الفرعية)
    apps_root = BASE_DIR / "apps"
    if apps_root.exists():
        for child in apps_root.iterdir():
            if child.is_dir() and (child / "apps.py").exists() and (child / "models.py").exists():
                found[child.name] = f"apps.{child.name}"
    return found

def snapshot():
    data = {
        "project_root": str(BASE_DIR),
        "settings_module": "config.settings",
        "scanned_at": datetime.datetime.utcnow().isoformat(),
        "apps": {},
        "admin_registered": [],
        "urls": [],
        "templates_presence": {},
        "missing_admin": [],
    }

    local_apps = find_local_apps()

    # التطبيقات + الموديلات
    for app_config in dj_apps.get_app_configs():
        label = app_config.label
        if label not in local_apps and not app_config.name.startswith(("apps.", "core")):
            continue
        models = [m.__name__ for m in app_config.get_models()]
        data["apps"][label] = {"module": app_config.name, "models": models}

    # المسجل في الأدمن
    for model in admin.site._registry.keys():
        data["admin_registered"].append(f"{model._meta.app_label}.{model.__name__}")

    # الناقص في الأدمن
    for label, info in data["apps"].items():
        for m in info["models"]:
            full = f"{label}.{m}"
            if full not in data["admin_registered"]:
                data["missing_admin"].append(full)

    # الروابط
    resolver = get_resolver()
    try:
        for pat in resolver.url_patterns:
            try:
                data["urls"].append(f"{pat.pattern} -> {pat.name or 'NoName'}")
            except Exception:
                pass
    except Exception:
        pass

    # القوالب
    for label, info in data["apps"].items():
        if info["module"] == "core":
            # ✅ التصحيح: مسار core الصحيح هو core/templates (بدون /core إضافية)
            tdir = BASE_DIR / "core" / "templates"
        else:
            parts = info["module"].split(".")
            if len(parts) == 2 and parts[0] == "apps":
                tdir = BASE_DIR / "apps" / parts[1] / "templates" / parts[1]
            else:
                tdir = BASE_DIR / "templates" / label
        exists = tdir.exists()
        files = []
        if exists:
            for p in tdir.rglob("*.html"):
                try:
                    files.append(str(p.relative_to(BASE_DIR)))
                except Exception:
                    files.append(str(p))
        data["templates_presence"][label] = {"dir_exists": exists, "files": files}

    return data

inventory = snapshot()

# project_meta المحدث
project_meta = {
    "project_root": inventory["project_root"],
    "settings_module": inventory["settings_module"],
    "apps": {label: info["models"] for label, info in inventory["apps"].items()},
    "scripts_folder": str(BASE_DIR),
    "last_script": "inventory_project.py",
    "scanned_at": inventory["scanned_at"],
}

with open(BASE_DIR / "project_meta.json", "w", encoding="utf-8") as f:
    json.dump(project_meta, f, indent=2, ensure_ascii=False)

with open(BASE_DIR / "project_inventory.json", "w", encoding="utf-8") as f:
    json.dump(inventory, f, indent=2, ensure_ascii=False)

# project_state
state_path = BASE_DIR / "project_state.json"
state = {
    "last_script": "inventory_project.py",
    "next_script": None,
    "status": "inventory_ready",
    "last_updated": inventory["scanned_at"],
}
if state_path.exists():
    try:
        prev = json.load(open(state_path, encoding="utf-8"))
        prev.update(state)
        state = prev
    except Exception:
        pass

with open(state_path, "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("✅ inventory_project: snapshots written (project_meta.json, project_inventory.json)")
