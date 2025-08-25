import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CORE_DIR = BASE_DIR / "apps" / "core"
REQUIRED_FILES = [
    CORE_DIR / "models.py",
    CORE_DIR / "forms.py",
    CORE_DIR / "filters.py",
    CORE_DIR / "serializers.py",
    CORE_DIR / "urls.py",
    CORE_DIR / "admin.py",
    CORE_DIR / "views"
]

missing = []

for path in REQUIRED_FILES:
    if not path.exists():
        missing.append(str(path.relative_to(BASE_DIR)))

templates_dir = CORE_DIR / "templates" / "core"
if not templates_dir.exists():
    missing.append(str(templates_dir.relative_to(BASE_DIR)))

if missing:
    print("❌ الملفات التالية مفقودة أو غير موجودة:")
    for m in missing:
        print(" -", m)
else:
    print("✅ كل ملفات core موجودة وجاهزة.")
