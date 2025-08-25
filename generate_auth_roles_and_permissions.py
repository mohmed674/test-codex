import os
import sys
import django
from datetime import datetime

# ✅ تهيئة بيئة Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import Group, Permission, User
from django.apps import apps
from django.db.models import signals
from django.contrib.auth import models as auth_models
import json

# ✅ تحميل التطبيقات والموديلات
with open(os.path.join(BASE_DIR, 'project_meta.json'), encoding='utf-8') as f:
    meta = json.load(f)

apps_data = meta.get("apps", {})

# ✅ الأدوار والصلاحيات
roles = {
    "Admin": ["add", "change", "delete", "view"],
    "Staff": ["add", "change", "view"],
    "Viewer": ["view"]
}

for role_name, perms in roles.items():
    group, _ = Group.objects.get_or_create(name=role_name)
    group.permissions.clear()

    for app_label, model_list in apps_data.items():
        for model_name in model_list:
            model = apps.get_model(app_label, model_name)
            for perm in perms:
                codename = f"{perm}_{model._meta.model_name}"
                permission = Permission.objects.filter(codename=codename).first()
                if permission:
                    group.permissions.add(permission)
                    print(f"✅ {role_name} ← {codename}")
                else:
                    print(f"⚠️ لم يتم العثور على: {codename}")

# ✅ تعطيل الإشارات مؤقتًا لتفادي الأخطاء أثناء إنشاء superadmin
signals.post_save.disconnect(dispatch_uid='alert_ai_on_user_change', sender=auth_models.User)

if not User.objects.filter(username='superadmin').exists():
    User.objects.create_superuser(username='superadmin', password='admin123', email='admin@example.com')
    print("✅ تم إنشاء superadmin")
else:
    print("ℹ️ superadmin موجود بالفعل")

# ✅ إعادة ربط الإشارة (اختياري)
try:
    from core.signals import alert_ai_on_user_change
    signals.post_save.connect(alert_ai_on_user_change, sender=auth_models.User, dispatch_uid='alert_ai_on_user_change')
except:
    pass

# ✅ تحديث حالة المشروع
project_state = {
    "last_script": "generate_auth_roles_and_permissions.py",
    "status": "roles_and_permissions_ready",
    "next_script": None,
    "last_updated": datetime.utcnow().isoformat()
}

with open(os.path.join(BASE_DIR, 'project_state.json'), 'w', encoding='utf-8') as f:
    json.dump(project_state, f, indent=2, ensure_ascii=False)
