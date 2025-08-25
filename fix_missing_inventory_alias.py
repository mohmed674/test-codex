from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
models_path = BASE / "apps" / "inventory" / "models.py"
src = models_path.read_text(encoding="utf-8")

# موجودة بالفعل؟
if re.search(r"\nclass\s+Inventory\s*\(", src):
    print("ℹ️ Inventory proxy already exists.")
else:
    # أضف Proxy على InventoryItem باسم Inventory بدون أي تغييرات على الجداول
    insertion = """

# ---- AUTO ALIAS (Proxy) ----
try:
    from .models import InventoryItem  # self-import guard if file split; fallback below
except Exception:
    pass

try:
    class Inventory(InventoryItem):  # proxy alias to satisfy imports
        class Meta:
            proxy = True
            verbose_name = "Inventory"
            verbose_name_plural = "Inventory"
except NameError:
    # Fallback when in same file scope
    class Inventory(InventoryItem):  # type: ignore[name-defined]
        class Meta:
            proxy = True
            verbose_name = "Inventory"
            verbose_name_plural = "Inventory"
# ---- END AUTO ALIAS ----
"""
    # نضيفه آخر الملف
    src = src.rstrip() + insertion
    models_path.write_text(src, encoding="utf-8")
    print("✅ Inventory proxy alias added to apps/inventory/models.py")
