import os
import sys
import django
from importlib import import_module

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib import admin
from django.apps import apps

# استيراد جميع الموديلات المسجلة في التطبيقات
app_configs = apps.get_app_configs()

for app_config in app_configs:
    try:
        models_module = import_module(f"{app_config.name}.models")
    except ModuleNotFoundError:
        continue

    for model in app_config.get_models():
        try:
            admin.site.register(model)
            print(f"✅ تم تسجيل: {model.__name__}")
        except admin.sites.AlreadyRegistered:
            print(f"ℹ️ {model.__name__} مسجّل مسبقًا")

print("✅ تم مزامنة جميع النماذج مع لوحة التحكم (admin).")
