from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
pkg_dir = BASE / "apps" / "suppliers" / "urls"
file_module = BASE / "apps" / "suppliers" / "urls.py"
main_py = pkg_dir / "main.py"
init_py = pkg_dir / "__init__.py"

# تأكد من وجود مجلد الحزمة
pkg_dir.mkdir(parents=True, exist_ok=True)

# لو عندنا ملف urls.py القديم على مستوى التطبيق: انقل محتواه إلى urls/main.py
if file_module.exists():
    src = file_module.read_text(encoding="utf-8")
    # تأمين include إلى المسار الصحيح داخل الحزمة
    src_fixed = re.sub(r"include\(['\"]suppliers\.api['\"]\)", "include('apps.suppliers.urls.api')", src)
    src_fixed = re.sub(r"include\(['\"]apps\.suppliers\.urls\.api['\"]\)", "include('apps.suppliers.urls.api')", src_fixed)
    main_py.write_text(src_fixed, encoding="utf-8")

# __init__.py ليصدّر urlpatterns من main.py
init_py.write_text("from .main import urlpatterns\n", encoding="utf-8")

print("✅ bridged: apps/suppliers/urls/__init__.py → exports urlpatterns from main.py")
