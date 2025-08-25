from pathlib import Path
import re

BASE = Path(__file__).resolve().parent

# 1) اجعل config/urls.py يضمّن المسار الصحيح
cfg = BASE / "config" / "urls.py"
src = cfg.read_text(encoding="utf-8")

# استبدل أي include('apps.suppliers.urls') بـ include('apps.suppliers.urls.main')
src = re.sub(r"include\(\s*['\"]apps\.suppliers\.urls['\"]\s*\)", "include('apps.suppliers.urls.main')", src)

# أنماط بديلة محتملة (tuple + namespace)
src = re.sub(
    r"include\(\(\s*['\"]apps\.suppliers\.urls['\"]\s*,\s*['\"]suppliers['\"]\s*\)\s*,\s*namespace\s*=\s*['\"]suppliers['\"]\s*\)",
    "include('apps.suppliers.urls.main')",
    src,
)

cfg.write_text(src, encoding="utf-8")

# 2) تأكد أن apps/suppliers/urls/main.py يعرّف urlpatterns صحيحة
main_p = BASE / "apps" / "suppliers" / "urls" / "main.py"
if not main_p.exists():
    main_p.parent.mkdir(parents=True, exist_ok=True)
    main_p.write_text("", encoding="utf-8")

m = main_p.read_text(encoding="utf-8")
if "urlpatterns" not in m:
    m = (
        "from django.urls import path, include\n"
        "# مسارات الموردين (واجهة وصفحات + API)\n"
        "urlpatterns = [\n"
        "    path('api/', include('apps.suppliers.urls.api')),\n"
        "]\n"
    )
else:
    # تأكد أن include لـ api موجود
    if "apps.suppliers.urls.api" not in m:
        # أضف السطر داخل القائمة إن أمكن
        m = re.sub(
            r"urlpatterns\s*=\s*\[\s*",
            "urlpatterns = [\n    path('api/', include('apps.suppliers.urls.api')),\n",
            m,
            count=1,
            flags=re.S,
        )
main_p.write_text(m, encoding="utf-8")

# 3) اجعل __init__.py فارغ لتجنّب دوّامة الاستيراد
init_p = BASE / "apps" / "suppliers" / "urls" / "__init__.py"
init_p.write_text("# empty to avoid circular imports\n", encoding="utf-8")

print("✅ suppliers routing stabilized (config include → main, main.py has urlpatterns, __init__ empty)")
