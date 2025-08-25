from pathlib import Path
import re, json, datetime

BASE = Path(__file__).resolve().parent
CFG = BASE / "config" / "urls.py"
STATE = BASE / "project_state.json"

src = CFG.read_text(encoding="utf-8")

# 1) حوّل أي include على صيغة tuple + namespace إلى include('module') فقط
#   أمثلة تُحوَّل:
#   include(('apps.sales.urls','sales'), namespace='sales')
#   include(("apps.sales.urls","sales"), namespace="sales")
tuple_ns_re = re.compile(
    r"include\(\(\s*['\"](?P<mod>[^'\"]+)['\"]\s*,\s*['\"][^'\"]+['\"]\s*\)\s*,\s*namespace\s*=\s*['\"][^'\"]+['\"]\s*\)"
)
src = tuple_ns_re.sub(lambda m: f"include('{m.group('mod')}')", src)

# 2) أزل أي وسيط namespace=… إن وُجد منفردًا
src = re.sub(r"include\(\s*(['\"][^'\"]+['\"])\s*,\s*namespace\s*=\s*['\"][^'\"]+['\"]\s*\)", r"include(\1)", src)

# 3) تنظيف مسافات مزدوجة وفواصل زائدة
src = re.sub(r",\s*\)", ")", src)

CFG.write_text(src, encoding="utf-8")

# تحديث الحالة
st = {"last_script": "strip_namespace_tuples.py", "status": "namespaces_stripped", "last_updated": datetime.datetime.utcnow().isoformat()}
try:
    prev = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    prev.update(st)
    st = prev
except: pass
STATE.write_text(json.dumps(st, indent=2, ensure_ascii=False), encoding="utf-8")

print("✅ Stripped namespace tuples from config/urls.py")
