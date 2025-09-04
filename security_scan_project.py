import json
import os
import re
from datetime import datetime

from load_project_context import load_context

context, state = load_context()
BASE_DIR = context["project_root"]
settings_module = context["settings_module"]
settings_path = os.path.join(BASE_DIR, settings_module.replace(".", "/")) + ".py"

issues = []

# 1️⃣ فحص إعدادات المشروع
with open(settings_path, "r", encoding="utf-8") as f:
    content = f.read()

if "DEBUG = True" in content:
    issues.append("❌ DEBUG مفعّل (يجب تعطيله في الإنتاج)")

if "ALLOWED_HOSTS = ['*']" in content or 'ALLOWED_HOSTS = ["*"]' in content:
    issues.append("❌ ALLOWED_HOSTS مفتوح للجميع")

if "SECRET_KEY =" in content:
    match = re.search(r'SECRET_KEY\s*=\s*[\'"](.+)[\'"]', content)
    if match and not match.group(1).startswith("os.environ"):
        issues.append("❌ SECRET_KEY مكشوف في الكود")

# 2️⃣ البحث في الملفات عن eval/exec ومفاتيح حساسة
dangerous = []
api_keys = []

for root, _, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
                if "eval(" in code:
                    dangerous.append(path)
                if "exec(" in code:
                    dangerous.append(path)
                if re.search(
                    r'(api|secret|token|key|password)[\'"\s]*[:=]', code, re.IGNORECASE
                ):
                    api_keys.append(path)

# دمج النتائج
if dangerous:
    issues.append(f"⚠️ استخدام eval/exec في: {len(dangerous)} ملف")
if api_keys:
    issues.append(f"⚠️ احتمال وجود مفاتيح حساسة في: {len(api_keys)} ملف")

# 3️⃣ إخراج التقرير
report = {
    "issues_found": issues,
    "files_with_eval_or_exec": dangerous,
    "files_with_possible_keys": api_keys,
    "scanned_at": datetime.utcnow().isoformat(),
}

report_path = os.path.join(BASE_DIR, "security_report.json")
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("✅ تم فحص المشروع أمنيًا.")
print("📄 التقرير: security_report.json")

# تحديث حالة المشروع
new_state = {
    "last_script": "security_scan_project.py",
    "next_script": None,
    "status": "secure_scan_complete",
    "last_updated": datetime.utcnow().isoformat(),
}
with open(os.path.join(BASE_DIR, "project_state.json"), "w", encoding="utf-8") as f:
    json.dump(new_state, f, indent=2, ensure_ascii=False)
