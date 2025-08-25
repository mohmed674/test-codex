from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
f = BASE / "apps" / "suppliers" / "urls.py"
src = f.read_text(encoding="utf-8")

# استبدال include('suppliers.api') بـ include('apps.suppliers.urls.api')
src2 = re.sub(r"include\(['\"]suppliers\.api['\"]\)", "include('apps.suppliers.urls.api')", src)

if src2 != src:
    f.write_text(src2, encoding="utf-8")
    print("✅ fixed suppliers include → apps.suppliers.urls.api")
else:
    print("ℹ️ no change")
