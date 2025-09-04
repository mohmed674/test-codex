# wire_urls.py
import json
import re
from pathlib import Path
from typing import List, Tuple

BASE_DIR = Path(__file__).resolve().parent
CONFIG_URLS = BASE_DIR / "config" / "urls.py"
BACKUP = BASE_DIR / "config" / "urls.autobackup.py"

# جمع كل التطبيقات التي لديها urls.py
candidates: List[Tuple[str, str, str]] = []

# core (جنب manage.py)
core_urls = BASE_DIR / "core" / "urls.py"
if core_urls.exists():
    # (label, module, prefix)
    candidates.append(("core", "core.urls", ""))  # مسار جذري أو يمكن تغييره لاحقًا

# apps/*
apps_root = BASE_DIR / "apps"
if apps_root.exists():
    for app_dir in sorted(p for p in apps_root.iterdir() if p.is_dir()):
        urls_py = app_dir / "urls.py"
        if urls_py.exists():
            label = app_dir.name
            module = f"apps.{label}.urls"
            candidates.append((label, module, f"{label}/"))  # /app/

# اقرأ config/urls.py
src = CONFIG_URLS.read_text(encoding="utf-8")

# نسخ احتياطي مرة واحدة
if not BACKUP.exists():
    BACKUP.write_text(src, encoding="utf-8")

# تأكد من الاستيرادات
need_imports: List[str] = []
if "from django.urls import path, include" not in src:
    need_imports.append("from django.urls import path, include")
if "from django.contrib import admin" not in src:
    need_imports.append("from django.contrib import admin")

if need_imports:
    # أدخل الاستيرادات بعد أول سطر import أو من بداية الملف
    lines = src.splitlines()
    insert_at = 0
    for i, line in enumerate(lines[:10]):
        if line.startswith("import") or line.startswith("from"):
            insert_at = i + 1
    for imp in reversed(need_imports):
        lines.insert(insert_at, imp)
    src = "\n".join(lines)

# تأكد من وجود urlpatterns
if "urlpatterns" not in src:
    src += "\n\nurlpatterns = []\n"


# جهّز الإدخالات المطلوبة
def has_include(s: str, module: str, prefix: str) -> bool:
    # نتحقق إن كان include موجودًا مسبقًا
    pat = re.escape(f"include('{module}')")
    if re.search(pat, s):
        return True
    # فحص بديل لو استُخدم دبل كوتس
    pat2 = re.escape(f'include("{module}")')
    if re.search(pat2, s):
        return True
    # فحص وجود path بنفس البادئة
    if prefix and re.search(rf"path\('{re.escape(prefix)}'", s):
        return True
    return False


inserts: List[str] = []
for label, module, prefix in candidates:
    if not has_include(src, module, prefix):
        if prefix == "":
            # core في الجذر
            inserts.append(f"    path('', include('{module}')),")
        else:
            inserts.append(f"    path('{prefix}', include('{module}')),")
        # نتأكد من وجود include في الاستيرادات إن لم يكن موجودًا
        # (تم التعامل معه أعلاه أيضًا)

if inserts:
    # أدخل العناصر داخل قائمة urlpatterns
    pattern = r"urlpatterns\s*=\s*\[(.*?)\]"
    m = re.search(pattern, src, flags=re.S)
    if m:
        start, end = m.span(1)
        before = src[:start]
        inside = m.group(1).strip()
        after = src[end:]
        new_inside = (inside + ("\n" if inside else "") + "\n".join(inserts)).strip()
        src = before + new_inside + after
    else:
        # أنماط مختلفة: نضيف سطر إنشاء ثم الإدراج
        src += "\nurlpatterns = [\n" + "\n".join(inserts) + "\n]\n"

# اكتب الملف
CONFIG_URLS.write_text(src, encoding="utf-8")

print("✅ urls wired successfully.")
print("📄 edited:", CONFIG_URLS)
print(
    "🗂️ includes:",
    json.dumps(
        [f"{prefix} -> {module}" for (label, module, prefix) in candidates],
        ensure_ascii=False,
        indent=2,
    ),
)
