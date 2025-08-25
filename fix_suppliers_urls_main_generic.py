from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
main_py = BASE / "apps" / "suppliers" / "urls" / "main.py"

src = main_py.read_text(encoding="utf-8")

# حوّل كل "from . import X" إلى "from apps.suppliers import X"
src = re.sub(r"from\s+\.\s+import\s+([A-Za-z0-9_]+)", r"from apps.suppliers import \1", src)

# حوّل كل "from .X import Y" إلى "from apps.suppliers.X import Y"
src = re.sub(r"from\s+\.\s*([A-Za-z0-9_]+)\s+import\s+([A-Za-z0-9_,\s]+)",
             r"from apps.suppliers.\1 import \2", src)

# ثبّت include(api) ليشير للحزمة الصحيحة
src = re.sub(r"include\(['\"]suppliers\.api['\"]\)", "include('apps.suppliers.urls.api')", src)
src = re.sub(r"include\(['\"]apps\.suppliers\.urls\.api['\"]\)", "include('apps.suppliers.urls.api')", src)

main_py.write_text(src, encoding="utf-8")
print("✅ normalized imports in apps/suppliers/urls/main.py")
