from pathlib import Path
import re

BASE = Path(__file__).resolve().parent

# 1) config/urls.py  → include('apps.suppliers.urls.main')
cfg = BASE / "config" / "urls.py"
src = cfg.read_text(encoding="utf-8")
src = re.sub(r"include\(['\"]apps\.suppliers\.urls['\"]\)", "include('apps.suppliers.urls.main')", src)
cfg.write_text(src, encoding="utf-8")

# 2) apps/suppliers/urls/__init__.py  → فارغ (لا يصدّر urlpatterns)
init_p = BASE / "apps" / "suppliers" / "urls" / "__init__.py"
if init_p.exists():
    init_p.write_text("# intentionally empty to avoid circular imports\n", encoding="utf-8")

# 3) apps/suppliers/urls/main.py  → استيراد صريح من الحزمة الأصلية
main_p = BASE / "apps" / "suppliers" / "urls" / "main.py"
m = main_p.read_text(encoding="utf-8")
m = re.sub(r"from\s+\.\s+import\s+([A-Za-z0-9_]+)", r"from apps.suppliers import \1", m)
m = re.sub(r"from\s+\.\s*([A-Za-z0-9_]+)\s+import\s+([A-Za-z0-9_,\s]+)", r"from apps.suppliers.\1 import \2", m)
m = re.sub(r"include\(['\"]suppliers\.api['\"]\)", "include('apps.suppliers.urls.api')", m)
main_p.write_text(m, encoding="utf-8")

# 4) apps/suppliers/urls/api.py  → from apps.suppliers import api_views
api_p = BASE / "apps" / "suppliers" / "urls" / "api.py"
if api_p.exists():
    a = api_p.read_text(encoding="utf-8")
    a = re.sub(r"from\s+\.\s+import\s+api_views", "from apps.suppliers import api_views", a)
    a = re.sub(r"from\s+\.\s*api_views\s+import\s+", "from apps.suppliers.api_views import ", a)
    api_p.write_text(a, encoding="utf-8")

print("✅ suppliers urls circular imports fixed.")
