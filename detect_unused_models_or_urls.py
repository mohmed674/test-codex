import os
import re
import django
import sys
import json

from load_project_context import load_context

context = load_context()
BASE_DIR = context['project_root']
os.environ.setdefault("DJANGO_SETTINGS_MODULE", context["settings_module"])
sys.path.append(BASE_DIR)
django.setup()

unused_models = {}
unused_url_names = []

# Step 1: تحليل كل الموديلات الموجودة حسب المشروع
all_models = {}
for app, models in context["apps"].items():
    for model in models:
        all_models[model] = {
            "app": app,
            "used_in": []
        }

# Step 2: تحليل ملفات المشروع
def scan_usage(root_path, keywords):
    usage = {key: False for key in keywords}
    for root, _, files in os.walk(root_path):
        for file in files:
            if file.endswith(('.py', '.html')):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    try:
                        content = f.read()
                        for key in keywords:
                            if key in content:
                                usage[key] = True
                    except:
                        continue
    return usage

# نبحث عن استخدام الموديلات
model_usage = scan_usage(BASE_DIR, list(all_models.keys()))
for model, used in model_usage.items():
    if not used:
        unused_models[model] = context["apps"][all_models[model]["app"]]

# Step 3: تحليل reverse URLs
def extract_url_names_from_templates(path):
    found = set()
    pattern = re.compile(r'{%\s*url\s+[\'"]([\w:-]+)[\'"]')
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".html"):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    found.update(pattern.findall(content))
    return found

used_url_names = extract_url_names_from_templates(os.path.join(BASE_DIR, 'templates'))

# Step 4: قارن مع أسماء URL الموجودة فعليًا
from django.urls import get_resolver
all_urls = get_resolver().reverse_dict.keys()
named_urls = set(name for name in all_urls if isinstance(name, str))

unused_url_names = list(named_urls - used_url_names)

# Step 5: حفظ التقرير
report = {
    "unused_models": unused_models,
    "unused_url_names": unused_url_names
}

with open(os.path.join(BASE_DIR, "unused_items_report.json"), "w", encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("✅ تم إنشاء تقرير بالعناصر غير المستخدمة.")
print("📄 الملف: unused_items_report.json")

# تحديث حالة المشروع
context["last_script"] = "detect_unused_models_or_urls.py"
with open(os.path.join(BASE_DIR, 'project_meta.json'), 'w', encoding='utf-8') as f:
    json.dump(context, f, indent=2, ensure_ascii=False)
