# detect_unused_models_or_urls.py
import json
import os
import re
import sys
from typing import Any, Dict, Iterable, List, Set

import django
from django.urls import get_resolver

# محاولة استيراد load_context، مع بديل آمن إذا لم يتوفر
try:
    from load_project_context import load_context as _load_ctx  # type: ignore
except Exception:

    def _load_ctx() -> Dict[str, Any]:
        # Fallback بسيط يسمح بتشغيل السكربت حتى بدون ملف السياق
        return {
            "project_root": os.getcwd(),
            "settings_module": os.environ.get(
                "DJANGO_SETTINGS_MODULE", "config.settings"
            ),
            "apps": {},
        }


# =========================
# Bootstrap Django context (robust)
# =========================
context: Dict[str, Any] = _load_ctx()
BASE_DIR: str = str(context.get("project_root", "."))
SETTINGS_MODULE: str = str(context.get("settings_module", "config.settings"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

django.setup()

# =========================
# Containers
# =========================
unused_models: Dict[str, List[str]] = {}
unused_url_names: List[str] = []

# Step 1: اجمع كل الموديلات من السياق
apps_map: Dict[str, List[str]] = dict(context.get("apps", {}))
all_models: Dict[str, Dict[str, Any]] = {}
for app_label, model_list in apps_map.items():
    for model_name in model_list:
        all_models[model_name] = {"app": app_label, "used_in": []}


# Step 2: فحص الاستخدام داخل الملفات
def scan_usage(root_path: str, keywords: Iterable[str]) -> Dict[str, bool]:
    usage: Dict[str, bool] = {key: False for key in keywords}
    for root, _, files in os.walk(root_path):
        for filename in files:
            if not (filename.endswith(".py") or filename.endswith(".html")):
                continue
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except (OSError, UnicodeDecodeError):
                continue
            for key in keywords:
                if not usage[key] and key in content:
                    usage[key] = True
    return usage


# حدد الموديلات غير المستخدمة
model_usage = scan_usage(BASE_DIR, list(all_models.keys()))
for model_name, used in model_usage.items():
    if not used:
        app_label = str(all_models[model_name]["app"])
        unused_models[model_name] = apps_map.get(app_label, [])


# Step 3: استخراج أسماء URL المستخدمة في القوالب
def extract_url_names_from_templates(path: str) -> Set[str]:
    found: Set[str] = set()
    pattern = re.compile(r'{%\s*url\s+[\'"]([\w:-]+)[\'"]')
    for root, _, files in os.walk(path):
        for filename in files:
            if not filename.endswith(".html"):
                continue
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except (OSError, UnicodeDecodeError):
                continue
            found.update(pattern.findall(content))
    return found


templates_dir = os.path.join(BASE_DIR, "templates")
used_url_names = extract_url_names_from_templates(templates_dir)

# Step 4: مقارنة أسماء URL الفعلية مع المستخدمة
all_urls = get_resolver().reverse_dict.keys()
named_urls = {name for name in all_urls if isinstance(name, str)}
unused_url_names = list(named_urls - used_url_names)

# Step 5: حفظ التقرير
report = {"unused_models": unused_models, "unused_url_names": unused_url_names}
with open(
    os.path.join(BASE_DIR, "unused_items_report.json"), "w", encoding="utf-8"
) as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("✅ تم إنشاء تقرير بالعناصر غير المستخدمة.")
print("📄 الملف: unused_items_report.json")

# تحديث حالة المشروع
context["last_script"] = "detect_unused_models_or_urls.py"
with open(os.path.join(BASE_DIR, "project_meta.json"), "w", encoding="utf-8") as f:
    json.dump(context, f, indent=2, ensure_ascii=False)
