import json
from datetime import datetime
from pathlib import Path

from load_project_context import load_context

context, state = load_context()
BASE_DIR = Path(context["project_root"])

# ✅ تم تعديل السطر هنا
SETTINGS_PATH = BASE_DIR / (context["settings_module"].replace(".", "/") + ".py")
ENV_PATH = BASE_DIR / ".env"
DEPLOY_CHECKS = []

# 1️⃣ تعديل DEBUG = False
with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
    content = f.read()

if "DEBUG = True" in content:
    content = content.replace("DEBUG = True", "DEBUG = False")
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    DEPLOY_CHECKS.append("✅ تم تعطيل DEBUG.")
else:
    DEPLOY_CHECKS.append("ℹ️ DEBUG معطّل بالفعل.")

# 2️⃣ التحقق من ALLOWED_HOSTS
if "ALLOWED_HOSTS = ['*']" in content or 'ALLOWED_HOSTS = ["*"]' in content:
    DEPLOY_CHECKS.append("❌ ALLOWED_HOSTS يسمح بالجميع! عدّله قبل النشر.")
else:
    DEPLOY_CHECKS.append("✅ ALLOWED_HOSTS مضبوط.")

# 3️⃣ إنشاء ملف .env
env_content = f"""# .env auto-generated
DJANGO_SETTINGS_MODULE={context["settings_module"]}
SECRET_KEY=change-me
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
"""

with open(ENV_PATH, "w", encoding="utf-8") as f:
    f.write(env_content)
DEPLOY_CHECKS.append("✅ تم إنشاء ملف .env")

# 4️⃣ فحص static/media
static_path = BASE_DIR / "static"
media_path = BASE_DIR / "media"
DEPLOY_CHECKS.append(f"📁 static موجود: {static_path.exists()}")
DEPLOY_CHECKS.append(f"📁 media موجود: {media_path.exists()}")

# 5️⃣ أوامر نشر مقترحة
DEPLOY_CHECKS.append("🚀 أوامر النشر المقترحة:")
DEPLOY_CHECKS.append("  python manage.py collectstatic --noinput")
DEPLOY_CHECKS.append("  python manage.py makemigrations && migrate")
DEPLOY_CHECKS.append("  python manage.py createsuperuser")
DEPLOY_CHECKS.append("  gunicorn config.wsgi:application --bind 0.0.0.0:8000")

# حفظ التقرير
report_path = BASE_DIR / "deploy_ready_report.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(DEPLOY_CHECKS, f, indent=2, ensure_ascii=False)

print("✅ تم إعداد المشروع للنشر.")
print(f"📄 التقرير: {report_path}")

# تحديث حالة المشروع
state["last_script"] = "prepare_for_deploy.py"
state["status"] = "ready_for_production"
state["next_script"] = None
state["last_updated"] = datetime.utcnow().isoformat()

with open(BASE_DIR / "project_state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
