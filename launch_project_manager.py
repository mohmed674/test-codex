import os
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
META_PATH = BASE_DIR / "project_meta.json"
STATE_PATH = BASE_DIR / "project_state.json"
SECURITY_REPORT_PATH = BASE_DIR / "security_report.json"

def load_file(path, name):
    if not path.exists():
        return f"❌ الملف '{name}' غير موجود"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return f"❌ فشل في قراءة '{name}'"

def show_header(title):
    print("\n" + "="*60)
    print(f"🔷 {title}")
    print("="*60)

def main():
    meta = load_file(META_PATH, "project_meta.json")
    state = load_file(STATE_PATH, "project_state.json")
    security = load_file(SECURITY_REPORT_PATH, "security_report.json") if SECURITY_REPORT_PATH.exists() else None

    # ✅ 1. معلومات المشروع
    show_header("معلومات المشروع")
    if isinstance(meta, dict):
        print(f"📁 جذر المشروع: {meta.get('project_root')}")
        print(f"⚙️ ملف الإعدادات: {meta.get('settings_module')}")
        print("📦 التطبيقات والموديلات:")
        for app, models in meta.get("apps", {}).items():
            print(f"  • {app}: {', '.join(models)}")
    else:
        print(meta)

    # ✅ 2. حالة المشروع
    show_header("حالة المشروع الحالية")
    if isinstance(state, dict):
        print(f"✅ آخر سكربت: {state.get('last_script')}")
        print(f"➡️ السكربت التالي: {state.get('next_script') or '🚩 لا يوجد - المشروع مكتمل'}")
        print(f"🕓 آخر تحديث: {state.get('last_updated')}")
        print(f"📌 الحالة: {state.get('status')}")
    else:
        print(state)

    # ✅ 3. تقرير الأمان (اختياري)
    if isinstance(security, dict):
        show_header("تقرير الأمان")
        issues = security.get("issues_found", [])
        if not issues:
            print("🔒 لا توجد مشاكل أمنية ملاحظة.")
        else:
            for issue in issues:
                print(issue)
    elif security:
        print(security)

    # ✅ 4. اقتراح الخطوة التالية
    show_header("اقتراح الإجراء التالي")
    if isinstance(state, dict):
        next_script = state.get("next_script")
        if next_script:
            print(f"✅ جاهز لتشغيل: python {next_script}")
        else:
            print("🎉 لا يوجد سكربت قادم محدد — المشروع مكتمل أو بانتظار إجراء جديد.")

    print("\n✅ جاهز دايمًا نخدمك يا معلم المعلمين.")

if __name__ == "__main__":
    main()
