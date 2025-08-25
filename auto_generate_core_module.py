import os
import sys
import json
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APPS_DIR = BASE_DIR / 'apps' / 'core'
META_PATH = BASE_DIR / 'project_meta.json'

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.append(str(BASE_DIR))
django.setup()

with open(META_PATH, 'r', encoding='utf-8') as f:
    meta = json.load(f)

models = meta['apps'].get('core', [])
print(f"✅ جاري توليد الملفات داخل apps/core/ لـ {len(models)} موديل...\n")

# 🔸 forms.py
forms_path = APPS_DIR / 'forms.py'
with open(forms_path, 'w', encoding='utf-8') as f:
    f.write("from django import forms\n")
    f.write("from .models import *\n\n")
    for model in models:
        f.write(f"class {model}Form(forms.ModelForm):\n")
        f.write(f"    class Meta:\n        model = {model}\n        fields = '__all__'\n\n")

# 🔸 filters.py
filters_path = APPS_DIR / 'filters.py'
with open(filters_path, 'w', encoding='utf-8') as f:
    f.write("import django_filters\n")
    f.write("from .models import *\n\n")
    for model in models:
        f.write(f"class {model}Filter(django_filters.FilterSet):\n")
        f.write(f"    class Meta:\n        model = {model}\n        fields = '__all__'\n\n")

# 🔸 serializers.py
serializers_path = APPS_DIR / 'serializers.py'
with open(serializers_path, 'w', encoding='utf-8') as f:
    f.write("from rest_framework import serializers\n")
    f.write("from .models import *\n\n")
    for model in models:
        f.write(f"class {model}Serializer(serializers.ModelSerializer):\n")
        f.write(f"    class Meta:\n        model = {model}\n        fields = '__all__'\n\n")

# 🔸 views.py
views_dir = APPS_DIR / 'views'
views_dir.mkdir(exist_ok=True)
for model in models:
    view_path = views_dir / f"{model.lower()}_views.py"
    with open(view_path, 'w', encoding='utf-8') as f:
        f.write("from django.views.generic import ListView, DetailView\n")
        f.write(f"from ..models import {model}\n\n")
        f.write(f"class {model}ListView(ListView):\n")
        f.write(f"    model = {model}\n    template_name = 'core/{model.lower()}_list.html'\n    context_object_name = '{model.lower()}_list'\n\n")
        f.write(f"class {model}DetailView(DetailView):\n")
        f.write(f"    model = {model}\n    template_name = 'core/{model.lower()}_detail.html'\n    context_object_name = '{model.lower()}'\n")

# 🔸 urls.py
urls_path = APPS_DIR / 'urls.py'
with open(urls_path, 'w', encoding='utf-8') as f:
    f.write("from django.urls import path\n")
    f.write("from .views import *\n\n")
    f.write("urlpatterns = [\n")
    for model in models:
        lname = model.lower()
        f.write(f"    path('{lname}/', {model}ListView.as_view(), name='{lname}_list'),\n")
        f.write(f"    path('{lname}/<int:pk>/', {model}DetailView.as_view(), name='{lname}_detail'),\n")
    f.write("]\n")

print("✅ تم توليد forms.py, filters.py, serializers.py, views/, urls.py بنجاح داخل apps/core/")

# تحديث الحالة
state = {
    "last_script": "auto_generate_core_module.py",
    "next_script": None,
    "status": "core_module_generated",
    "last_updated": str(Path().stat().st_mtime)
}
with open(BASE_DIR / 'project_state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
