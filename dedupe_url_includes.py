from pathlib import Path
import re, json, datetime

BASE = Path(__file__).resolve().parent
CFG = BASE / "config" / "urls.py"
STATE = BASE / "project_state.json"

src = CFG.read_text(encoding="utf-8")

# التعرّف على سطور include داخل urlpatterns
# مثال مطابق: path('sales/', include('apps.sales.urls')),
pat_list_block = re.compile(r"(urlpatterns\s*=\s*\[)(.*?)(\])", re.S)
m = pat_list_block.search(src)
if not m:
    print("❌ لم يتم العثور على urlpatterns في config/urls.py")
    raise SystemExit(1)

head, body, tail = m.group(1), m.group(2), m.group(3)

# اجلب كل الأسطر للمعالجة
lines = [ln for ln in body.splitlines()]

include_re = re.compile(r"include\(\s*['\"]([^'\"]+)['\"]\s*\)")
seen = set()
new_lines = []
removed = []

for ln in lines:
    mo = include_re.search(ln)
    if not mo:
        new_lines.append(ln)
        continue
    target = mo.group(1).strip()

    # طبيعـة التضمينات المقبولة:
    # - apps.<app>.urls
    # - apps.suppliers.urls.main
    # - core.urls
    # إن كان التضمين مكررًا لنفس الـ target نتخلص من الإعادة
    if target in seen:
        # احذف التضمينات المكررة التي تسبب تضارب namespaces
        removed.append(ln.strip())
        continue
    seen.add(target)

    # إزالة أي namespace/tuple قد يسبب تضارب (نحوّلها دائمًا لصيغة include('module') فقط)
    # مثال: include(( 'apps.sales.urls', 'sales'), namespace='sales')  ← نحولها
    ln = re.sub(r"include\(\(\s*['\"][^'\"]+['\"].*?\)\s*,\s*namespace\s*=\s*['\"][^'\"]+['\"]\s*\)", f"include('{target}')", ln)
    new_lines.append(ln)

# أعِدّ بناء الملف
new_body = "\n".join([ln for ln in new_lines if ln.strip()]) + "\n"
fixed = src[:m.start(2)] + new_body + src[m.end(2):]
CFG.write_text(fixed, encoding="utf-8")

# تحديث حالة المشروع
st = {"last_script": "dedupe_url_includes.py", "status": "urls_deduped", "last_updated": datetime.datetime.utcnow().isoformat()}
try:
    prev = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    prev.update(st)
    st = prev
except: pass
STATE.write_text(json.dumps(st, indent=2, ensure_ascii=False), encoding="utf-8")

print("✅ De-duplicated include targets in config/urls.py")
if removed:
    print("🧹 Removed duplicates:")
    for r in removed:
        print(" -", r)
