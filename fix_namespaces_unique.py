from pathlib import Path
import re, json, datetime

BASE = Path(__file__).resolve().parent
CFG = BASE / "config" / "urls.py"
STATE = BASE / "project_state.json"

src = CFG.read_text(encoding="utf-8")

# 1) اجعل كل تضمين لملفات API يستخدم namespace فريد <app>_api
#    أمثلة مستهدفة:
#    include('apps.sales.api_urls')
#    include('apps.sales.urls.api')
api_patterns = [
    r"include\(\s*['\"]apps\.(?P<app>[a-zA-Z0-9_]+)\.api_urls['\"]\s*\)",
    r"include\(\s*['\"]apps\.(?P<app>[a-zA-Z0-9_]+)\.urls\.api['\"]\s*\)",
]

def repl(m):
    app = m.group("app")
    module = m.group(0)
    # استخرج المسار الحقيقي للموديل من الـ match الأصلي:
    mod = re.search(r"['\"](apps\.[^'\"]+)['\"]", module).group(1)
    return f"include(('{mod}', '{app}_api'), namespace='{app}_api')"

for pat in api_patterns:
    src = re.sub(pat, repl, src)

# 2) أزِل التكرارات لنفس namespace إن ظهرت
#    (نكتفي بأول ظهور لكل ('mod','ns'), namespace='ns')
lines = src.splitlines()
seen_ns = set()
new_lines = []
ns_line_re = re.compile(r"include\(\(\s*['\"](?P<mod>[^'\"]+)['\"]\s*,\s*['\"](?P<ns>[^'\"]+)['\"]\s*\)\s*,\s*namespace\s*=\s*['\"](?P<ns2>[^'\"]+)['\"]\s*\)")
for ln in lines:
    m = ns_line_re.search(ln)
    if not m:
        new_lines.append(ln)
        continue
    ns = m.group("ns")
    if ns in seen_ns:
        # احذف السطر المكرر
        continue
    seen_ns.add(ns)
    new_lines.append(ln)
src = "\n".join(new_lines)

# 3) احفظ الملف
CFG.write_text(src, encoding="utf-8")

# 4) حدث حالة المشروع
st = {"last_script": "fix_namespaces_unique.py", "status": "namespaces_unique", "last_updated": datetime.datetime.utcnow().isoformat()}
try:
    prev = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    prev.update(st)
    st = prev
except: pass
STATE.write_text(json.dumps(st, indent=2, ensure_ascii=False), encoding="utf-8")

print("✅ Namespaces for API includes are now unique (…_api) and deduped.")
