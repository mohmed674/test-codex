import os
import sys
import json
import django
from load_project_context import load_context

context = load_context()
BASE_DIR = context["project_root"]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", context["settings_module"])
sys.path.append(BASE_DIR)
django.setup()

# ملف الإخراج النهائي
output_path = os.path.join(BASE_DIR, "generated_api_code.py")

lines = []
lines.append("from rest_framework import serializers, generics")
lines.append("from django.urls import path\n")

# بناء الاستيرادات
for app, models in context["apps"].items():
    lines.append(f"from {app}.models import {', '.join(models)}")

# بناء serializers
lines.append("\n# 🔹 Serializers")
for app, models in context["apps"].items():
    for model in models:
        lines.append(f"""
class {model}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {model}
        fields = '__all__'
""")

# بناء views
lines.append("\n# 🔹 Views")
for app, models in context["apps"].items():
    for model in models:
        lines.append(f"""
class {model}ListView(generics.ListAPIView):
    queryset = {model}.objects.all()
    serializer_class = {model}Serializer

class {model}DetailView(generics.RetrieveAPIView):
    queryset = {model}.objects.all()
    serializer_class = {model}Serializer
""")

# بناء URLs
lines.append("\n# 🔹 URL patterns")
lines.append("urlpatterns = [")
for app, models in context["apps"].items():
    for model in models:
        name = model.lower()
        lines.append(f"    path('{name}/', {model}ListView.as_view(), name='{name}-list'),")
        lines.append(f"    path('{name}/<int:pk>/', {model}DetailView.as_view(), name='{name}-detail'),")
lines.append("]\n")

# كتابة الملف
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print("✅ تم توليد الكود الخاص بـ DRF (Serializers + Views + URLs)")
print(f"📄 الملف الناتج: {output_path}")

# تحديث حالة المشروع
context["last_script"] = "auto_generate_serializers_and_views.py"
with open(os.path.join(BASE_DIR, 'project_meta.json'), 'w', encoding='utf-8') as f:
    json.dump(context, f, indent=2, ensure_ascii=False)
