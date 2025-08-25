from pathlib import Path

BASE = Path(__file__).resolve().parent
cfg = BASE / "config" / "urls.py"

minimal = """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # واجهة النظام الأساسية من core فقط (كل الباقي متوقف مؤقتًا)
    path('', include('core.urls')),
]
"""

cfg.write_text(minimal, encoding="utf-8")
print("✅ config/urls.py reset to minimal (admin + core).")
