import os
import django
import sys
import json
from load_project_context import load_context

context = load_context()
BASE_DIR = context["project_root"]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", context["settings_module"])
sys.path.append(BASE_DIR)
django.setup()

from importlib import import_module

missing_admin = {}
admin_snippets = []
missing_urls = {}
url_snippets = []

for app, models in context["apps"].items():
    try:
        admin_module = import_module(f"{app}.admin")
        admin_code = open(os.path.join(BASE_DIR, app, 'admin.py'), encoding='utf-8').read()
    except:
        admin_code = ""
    
    try:
        urls_path = os.path.join(BASE_DIR, app, 'urls.py')
        if os.path.exists(urls_path):
            urls_code = open(urls_path, encoding='utf-8').read()
        else:
            urls_code = ""
    except:
        urls_code = ""

    for model in models:
        if f"{model}Admin" not in admin_code:
            missing_admin.setdefault(app, []).append(model)
            admin_snippets.append(f"""
@admin.register({model})
class {model}Admin(admin.ModelAdmin):
    list_display = ['id']
""")

        if f"path('{model.lower()}/'" not in urls_code:
            missing_urls.setdefault(app, []).append(model)
            url_snippets.append(f"""
from django.urls import path
from . import views

urlpatterns += [
    path('{model.lower()}/', views.{model}ListView.as_view(), name='{model.lower()}_list'),
    path('{model.lower()}/<int:pk>/', views.{model}DetailView.as_view(), name='{model.lower()}_detail'),
]
""")

# ✏️ توليد الملف النهائي
output_file = os.path.join(BASE_DIR, "generated_admin_and_urls_snippets.py")
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# ✅ Snippets to add missing admin registrations:\n")
    f.write("from django.contrib import admin\n")
    for app in context["apps"]:
        f.write(f"from {app}.models import " + ", ".join(context["apps"][app]) + "\n")
    f.write("\n".join(admin_snippets))

    f.write("\n\n# ✅ Snippets to add missing URL patterns:\n")
    f.write("\n".join(url_snippets))

print("✅ تم توليد كود التسجيل في admin.py و urls.py")
print("📄 الملف الناتج: generated_admin_and_urls_snippets.py")

# تحديث حالة المشروع
context["last_script"] = "generate_missing_urls_or_admin.py"
with open(os.path.join(BASE_DIR, 'project_meta.json'), 'w', encoding='utf-8') as f:
    json.dump(context, f, indent=2, ensure_ascii=False)
