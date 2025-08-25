# mrp/tasks.py

from .models import MaterialPlanning, MaterialLine
from apps.production.models import BillOfMaterials
from apps.inventory.models import InventoryItem
from django.db.models import Sum
from datetime import date

def auto_generate_planning():
    upcoming = []  # توقعات الإنتاج من AI
    for item in upcoming:
        MaterialPlanning.objects.create(...)
