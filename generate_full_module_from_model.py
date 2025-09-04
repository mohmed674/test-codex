# generate_full_module_from_model.py
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import django

from load_project_context import load_context

# =========================
# Bootstrap Django
# =========================
context, state = load_context()
BASE_DIR = Path(context["project_root"])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", context["settings_module"])
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
django.setup()

# === إعدادات ===
TARGET_MODEL = "Customer"  # ← غيّر دي لأي موديل تاني

# البحث عن التطبيق اللي يحتوي الموديل
app_name = None
for app, models in context["apps"].items():
    if TARGET_MODEL in models:
        app_name = app
        break

if not app_name:
    print(f"❌ لم يتم العثور على الموديل: {TARGET_MODEL}")
    sys.exit(1)

# توليد كل الأجزاء
code_output: list[str] = []

code_output.append(f"# ✅ وحدة كاملة لموديل: {TARGET_MODEL} من التطبيق: {app_name}\n")

# 1. Form
code_output.append(
    f"""from django import forms
from {app_name}.models import {TARGET_MODEL}

class {TARGET_MODEL}Form(forms.ModelForm):
    class Meta:
        model = {TARGET_MODEL}
        fields = '__all__'
"""
)

# 2. Filter
code_output.append(
    f"""import django_filters

class {TARGET_MODEL}Filter(django_filters.FilterSet):
    class Meta:
        model = {TARGET_MODEL}
        fields = '__all__'
"""
)

# 3. Views
code_output.append(
    f"""from django.views.generic import ListView, DetailView

class {TARGET_MODEL}ListView(ListView):
    model = {TARGET_MODEL}
    template_name = '{app_name}/{TARGET_MODEL.lower()}_list.html'
    context_object_name = '{TARGET_MODEL.lower()}_list'

class {TARGET_MODEL}DetailView(DetailView):
    model = {TARGET_MODEL}
    template_name = '{app_name}/{TARGET_MODEL.lower()}_detail.html'
    context_object_name = '{TARGET_MODEL.lower()}'
"""
)

# 4. URLs
code_output.append(
    f"""from django.urls import path
from .views import {TARGET_MODEL}ListView, {TARGET_MODEL}DetailView

urlpatterns = [
    path('{TARGET_MODEL.lower()}/', {TARGET_MODEL}ListView.as_view(), name='{TARGET_MODEL.lower()}_list'),
    path('{TARGET_MODEL.lower()}/<int:pk>/', {TARGET_MODEL}DetailView.as_view(), name='{TARGET_MODEL.lower()}_detail'),
]
"""
)

# 5. Admin
code_output.append(
    f"""from django.contrib import admin
from .models import {TARGET_MODEL}

@admin.register({TARGET_MODEL})
class {TARGET_MODEL}Admin(admin.ModelAdmin):
    list_display = ['id']
"""
)

# 6. Serializer
code_output.append(
    f"""from rest_framework import serializers

class {TARGET_MODEL}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {TARGET_MODEL}
        fields = '__all__'
"""
)

# 7. Template
code_output.append(
    f"""<!-- {TARGET_MODEL.lower()}_list.html -->
<h1>قائمة {TARGET_MODEL}</h1>
<ul>
  {{% for item in {TARGET_MODEL.lower()}_list %}}
    <li>{{{{ item }}}}</li>
  {{% endfor %}}
</ul>
"""
)

# حفظ الملف
output_path = BASE_DIR / f"generated_full_module_{TARGET_MODEL.lower()}.py"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n\n".join(code_output))

print(f"✅ تم توليد وحدة كاملة لموديل {TARGET_MODEL} في الملف:")
print(f"📄 {output_path}")

# تحديث حالة المشروع
new_state = {
    "last_script": "generate_full_module_from_model.py",
    "next_script": None,
    "status": f"{TARGET_MODEL}_module_ready",
    "last_updated": datetime.utcnow().isoformat(),
}
with open(BASE_DIR / "project_state.json", "w", encoding="utf-8") as f:
    json.dump(new_state, f, indent=2, ensure_ascii=False)
