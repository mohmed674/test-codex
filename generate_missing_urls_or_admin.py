# generate_missing_urls_or_admin.py
import json
import os
import sys
from contextlib import suppress
from importlib import import_module
from typing import Any, Dict, List

import django

# ✅ استيراد آمن لـ load_context مع بديل (fallback) إذا لم يتوفر
try:
    from load_project_context import load_context as _load_ctx  # type: ignore
except Exception:

    def _load_ctx() -> Dict[str, Any]:
        return {
            "project_root": os.getcwd(),
            "settings_module": os.environ.get(
                "DJANGO_SETTINGS_MODULE", "config.settings"
            ),
            "apps": {},
        }


# =========================
# Bootstrap Django
# =========================
context: Dict[str, Any] = _load_ctx()
BASE_DIR: str = str(context.get("project_root", os.getcwd()))
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", str(context.get("settings_module", "config.settings"))
)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
django.setup()

# =========================
# Containers
# =========================
missing_admin: Dict[str, List[str]] = {}
admin_snippets: List[str] = []
missing_urls: Dict[str, List[str]] = {}
url_snippets: List[str] = []


def read_text_safe(path: str) -> str:
    """قراءة ملف نصي بأمان مع إرجاع نص فارغ عند الفشل."""
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ""


# =========================
# Scan apps from context
# =========================
for app, models in context.get("apps", {}).items():
    # admin.py code
    with suppress(Exception):
        import_module(f"{app}.admin")
    admin_path = os.path.join(BASE_DIR, app, "admin.py")
    admin_code = read_text_safe(admin_path)

    # urls.py code
    urls_path = os.path.join(BASE_DIR, app, "urls.py")
    urls_code = read_text_safe(urls_path)

    for model in models:
        # ----- Admin missing?
        if f"{model}Admin" not in admin_code:
            missing_admin.setdefault(app, []).append(model)
            admin_snippets.append(
                f"""
@admin.register({model})
class {model}Admin(admin.ModelAdmin):
    list_display = ['id']
"""
            )

        # ----- URLs missing?
        if f"path('{model.lower()}/'" not in urls_code:
            missing_urls.setdefault(app, []).append(model)
            url_snippets.append(
                f"""
from django.urls import path
from . import views

urlpatterns += [
    path('{model.lower()}/', views.{model}ListView.as_view(), name='{model.lower()}_list'),
    path('{model.lower()}/<int:pk>/', views.{model}DetailView.as_view(), name='{model.lower()}_detail'),
]
"""
            )

# =========================
# Write output snippets
# =========================
output_file = os.path.join(BASE_DIR, "generated_admin_and_urls_snippets.py")
with open(output_file, "w", encoding="utf-8") as f:
    f.write("# ✅ Snippets to add missing admin registrations:\n")
    f.write("from django.contrib import admin\n")
    for app in context.get("apps", {}):
        models_list = ", ".join(context["apps"][app])
        f.write(f"from {app}.models import {models_list}\n")
    f.write("\n".join(admin_snippets))

    f.write("\n\n# ✅ Snippets to add missing URL patterns:\n")
    f.write("\n".join(url_snippets))

print("✅ تم توليد كود التسجيل في admin.py و urls.py")
print(f"📄 الملف الناتج: {output_file}")

# =========================
# Update project meta
# =========================
context["last_script"] = "generate_missing_urls_or_admin.py"
with open(os.path.join(BASE_DIR, "project_meta.json"), "w", encoding="utf-8") as f:
    json.dump(context, f, indent=2, ensure_ascii=False)
