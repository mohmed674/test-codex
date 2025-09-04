# register_core_missing_admin.py
import os
import sys
from contextlib import suppress

import django
from django.contrib import admin

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def get_core_models():
    # استيراد داخل الدالة لتجنب E402 ولضمان تهيئة Django قبل استيراد الموديلات
    from core.models import Client, Department, Employee, SmartAccountTemplate

    return Department, Employee, Client, SmartAccountTemplate


def safe_register(model) -> None:
    try:
        admin.site.register(model)
        print(f"✅ Registered: {model.__name__}")
    except admin.sites.AlreadyRegistered:
        print(f"ℹ️ Already registered: {model.__name__}")


def main() -> None:
    Department, Employee, Client, SmartAccountTemplate = get_core_models()
    safe_register(Department)
    safe_register(Employee)
    safe_register(Client)
    safe_register(SmartAccountTemplate)
    print("✅ Done.")


if __name__ == "__main__":
    with suppress(Exception):
        main()
