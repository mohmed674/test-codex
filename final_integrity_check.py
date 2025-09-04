import json
from datetime import datetime
from pathlib import Path

from load_project_context import load_context

# تحميل السياق
context, state = load_context()
BASE_DIR = Path(context["project_root"])
issues = []

# 1. فحص الملفات الأساسية
required_files = [
    BASE_DIR / "project_meta.json",
    BASE_DIR / "project_state.json",
    BASE_DIR / "deploy_ready_report.json",
    BASE_DIR / "security_report.json",
]

for f in required_files:
    if not f.exists():
        issues.append(f"❌ مفقود: {f.name}")
    else:
        issues.append(f"✅ موجود: {f.name}")

# 2. فحص مجلدات المشروع
required_dirs = ["static", "media", "templates"]
for d in required_dirs:
    path = BASE_DIR / d
    if not path.exists():
        issues.append(f"❌ المجلد غير موجود: {d}/")
    else:
        issues.append(f"✅ المجلد موجود: {d}/")

# 3. تأكيد وجود الموديلات داخل تطبيقات موجودة
for app, models in context["apps"].items():
    app_path = BASE_DIR / app
    if not app_path.exists():
        issues.append(f"❌ التطبيق '{app}' غير موجود فعليًا في المشروع.")
    else:
        issues.append(f"✅ التطبيق '{app}' موجود ويتضمن: {', '.join(models)}")

# 4. سكربتات أساسية اشتغلت؟
required_scripts = [
    "analyze_project.py",
    "sync_admin_with_fixed_models_and_urls.py",
    "generate_auth_roles_and_permissions.py",
    "prepare_for_deploy.py",
    "security_scan_project.py",
]
for script in required_scripts:
    if script == state.get("last_script") or script in state.get("last_script", ""):
        issues.append(f"✅ السكربت '{script}' تم تنفيذه")
    else:
        issues.append(f"ℹ️ تأكد من تنفيذ السكربت: {script}")

# 5. تقرير نهائي
report = {"check_time": datetime.utcnow().isoformat(), "result": issues}

report_path = BASE_DIR / "final_integrity_report.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("✅ تم تنفيذ فحص التكامل النهائي.")
print(f"📄 التقرير: {report_path}")

# تحديث الحالة
state["last_script"] = "final_integrity_check.py"
state["status"] = "integrity_verified"
state["next_script"] = None
state["last_updated"] = datetime.utcnow().isoformat()

with open(BASE_DIR / "project_state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
