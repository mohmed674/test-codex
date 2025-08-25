from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
main_py = BASE / "apps" / "suppliers" / "urls" / "main.py"

src = main_py.read_text(encoding="utf-8")

# استبدالات لتجنب الاستيراد الدائري من الحزمة نفسها
src = re.sub(r"\bfrom\s+\.?\s*import\s+supplier_views\b", "from apps.suppliers import supplier_views", src)
src = re.sub(r"\bfrom\s+\.?\s*import\s+views\b", "from apps.suppliers import views", src)

# لو في include للـ api داخل نفس الحزمة يظل كما هو أو نحوله لاستيراد مباشر للأنماط
# (اختياري) اجعل تضمين api أكثر متانة دون تكرار التحميل
src = re.sub(
    r"include\(['\"]apps\.suppliers\.urls\.api['\"]\)",
    "include('apps.suppliers.urls.api')",
    src
)

main_py.write_text(src, encoding="utf-8")
print("✅ fixed imports in apps/suppliers/urls/main.py")

