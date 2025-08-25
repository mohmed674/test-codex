import os
import sys
import django
import json
from load_project_context import load_context

context = load_context()
BASE_DIR = context["project_root"]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", context["settings_module"])
sys.path.append(BASE_DIR)
django.setup()

output_path = os.path.join(BASE_DIR, "generated_forms_and_filters.py")

lines = []
lines.append("from django import forms")
lines.append("import django_filters\n")

# استيراد الموديلات
for app, models in context["apps"].items():
    lines.append(f"from {app}.models import {', '.join(models)}")

# توليد ModelForms
lines.append("\n# 🔹 ModelForms")
for app, models in context["apps"].items():
    for model in models:
        lines.append(f"""
class {model}Form(forms.ModelForm):
    class Meta:
        model = {model}
        fields = '__all__'
""")

# توليد Filters
lines.append("\n# 🔹 DjangoFilterSet")
for app, models in context["apps"].items():
    for model in models:
        lines.append(f"""
class {model}Filter(django_filters.FilterSet):
    class Meta:
        model = {model}
        fields = '__all__'
""")

# حفظ الملف
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print("✅ تم توليد ModelForms و Filters")
print(f"📄 الملف الناتج: {output_path}")

# تحديث حالة المشروع
context["last_script"] = "auto_generate_forms_and_filters.py"
with open(os.path.join(BASE_DIR, 'project_meta.json'), 'w', encoding='utf-8') as f:
    json.dump(context, f, indent=2, ensure_ascii=False)
