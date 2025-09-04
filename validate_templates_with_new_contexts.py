import json
import os
import re
import sys

import django

# ⬅️ تحميل السياق العام للمشروع
from load_project_context import load_context

context = load_context()
BASE_DIR = context["project_root"]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", context["settings_module"])
sys.path.append(BASE_DIR)
django.setup()

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

missing_context = {}


def extract_template_vars(template_path):
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    return set(re.findall(r"{{\s*(\w+)\s*}}", content))


for root, _, files in os.walk(TEMPLATES_DIR):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            vars_found = extract_template_vars(path)

            # ⚠️ افتراض مؤقت: نحتاج نربطها بـ view لاحقًا (تحسين)
            # نسجل فقط إن المتغيرات دي موجودة في القالب
            missing_context[path] = list(vars_found)

# 🔁 حفظ النتائج
with open(
    os.path.join(BASE_DIR, "missing_template_context.json"), "w", encoding="utf-8"
) as f:
    json.dump(missing_context, f, indent=2, ensure_ascii=False)

print("✅ تم استخراج المتغيرات من جميع القوالب.")
print("📄 الملف الناتج: missing_template_context.json")

# 🧠 تحديث المشروع الحالي
context["last_script"] = "validate_templates_with_new_contexts.py"
with open(os.path.join(BASE_DIR, "project_meta.json"), "w", encoding="utf-8") as f:
    json.dump(context, f, indent=2, ensure_ascii=False)
