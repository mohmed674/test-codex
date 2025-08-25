import os, sys, django
from django.contrib import admin

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Department, Employee, Client, SmartAccountTemplate

def safe_register(model):
    try:
        admin.site.register(model)
        print(f"✅ Registered: {model.__name__}")
    except admin.sites.AlreadyRegistered:
        print(f"ℹ️ Already registered: {model.__name__}")

safe_register(Department)
safe_register(Employee)
safe_register(Client)
safe_register(SmartAccountTemplate)

print("✅ Done.")
