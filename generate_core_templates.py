import os, sys, json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CORE_TPL_DIR = BASE_DIR / "core" / "templates" / "core"
INV_PATH = BASE_DIR / "project_inventory.json"
STATE_PATH = BASE_DIR / "project_state.json"

CORE_TPL_DIR.mkdir(parents=True, exist_ok=True)

# قراءة نماذج core من تقرير الجرد
with open(INV_PATH, encoding="utf-8") as f:
    inv = json.load(f)

core_models = inv.get("apps", {}).get("core", {}).get("models", [])

# base.html
(CORE_TPL_DIR / "base.html").write_text(
"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{% block title %}Core{% endblock %}</title>
<link rel="stylesheet" href="/static/css/erp.css">
<style>
body{font-family:system-ui,Segoe UI,Arial;padding:16px;background:#fff}
h1,h2{margin:0 0 12px}
table{width:100%;border-collapse:collapse}
th,td{border:1px solid #ddd;padding:8px}
thead{background:#f5f5f5}
a.button{display:inline-block;padding:8px 12px;border:1px solid #888;border-radius:6px;text-decoration:none}
</style>
</head>
<body>
<header><h1>{% block header %}لوحة Core{% endblock %}</h1></header>
<main>{% block content %}{% endblock %}</main>
</body></html>
""", encoding="utf-8"
)

# قوالب عامة بلا {% url %} لتفادي NoReverseMatch
LIST_TMPL = """{% extends "core/base.html" %}
{% block title %}{{ model_name }} - قائمة{% endblock %}
{% block content %}
<h2>قائمة {{ model_name }}</h2>
<table>
  <thead><tr><th>#</th><th>المعرف</th><th>العرض</th></tr></thead>
  <tbody>
    {% for obj in object_list %}
      <tr>
        <td>{{ forloop.counter }}</td>
        <td>{{ obj.pk }}</td>
        <td><a class="button" href="javascript:history.back()">رجوع</a></td>
      </tr>
    {% empty %}
      <tr><td colspan="3">لا توجد بيانات</td></tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
"""

DETAIL_TMPL = """{% extends "core/base.html" %}
{% block title %}{{ model_name }} - تفاصيل{% endblock %}
{% block content %}
<h2>تفاصيل {{ model_name }}</h2>
<pre style="white-space:pre-wrap">{{ object }}</pre>
<a class="button" href="javascript:history.back()">عودة</a>
{% endblock %}
"""

created = []

for model in core_models:
    model_lower = model.lower()
    list_path = CORE_TPL_DIR / f"{model_lower}_list.html"
    detail_path = CORE_TPL_DIR / f"{model_lower}_detail.html"

    if not list_path.exists():
        list_path.write_text(LIST_TMPL, encoding="utf-8")
        created.append(str(list_path.relative_to(BASE_DIR)))
    if not detail_path.exists():
        detail_path.write_text(DETAIL_TMPL, encoding="utf-8")
        created.append(str(detail_path.relative_to(BASE_DIR)))

# لوحة بسيطة تعرض روابط افتراضية بالأسماء فقط (نصًا) لتجنب عكس الروابط
dashboard = CORE_TPL_DIR / "dashboard.html"
if not dashboard.exists():
    dashboard.write_text(
"""{% extends "core/base.html" %}
{% block title %}لوحة Core{% endblock %}
{% block content %}
<h2>لوحة Core</h2>
<ul>
{% for m in core_models %}
  <li>{{ m }} — قائمة: {{ m|lower }}_list • تفاصيل: {{ m|lower }}_detail</li>
{% endfor %}
</ul>
{% endblock %}
""", encoding="utf-8")

# تحديث حالة المشروع
state = {
    "last_script": "generate_core_templates.py",
    "next_script": None,
    "status": "core_templates_ready",
}
try:
    prev = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {}
    prev.update(state)
    state = prev
except:
    pass
STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

print("✅ generated:")
for p in created:
    print("-", p)
