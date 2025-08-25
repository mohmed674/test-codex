# ERP_CORE/production/smart_master.py

from apps.products.models import Product
from apps.inventory.models import InventoryItem

# ✅ Smart Master: المواد الخام المطلوبة لكل منتج
# مفتاح الربط بين المنتج وأوامر التشغيل والمخزون

def get_required_materials(product_name):
    """
    تُرجع قائمة الخامات المطلوبة وكمياتها لكل منتج من جدول InventoryItem
    بناءً على اسم المنتج الموجود في جدول Product.
    """
    try:
        product = Product.objects.get(name=product_name)
    except Product.DoesNotExist:
        return []

    # مثال: نربط اسم المنتج بالمواد الخام حسب وحدة التصنيع
    material_definitions = {
        "قميص رجالي": [
            {"material": "قماش قطن", "quantity": 2.5, "unit": "متر"},
            {"material": "زرار", "quantity": 5, "unit": "قطعة"},
        ],
        "بنطلون جينز": [
            {"material": "قماش جينز", "quantity": 3.0, "unit": "متر"},
            {"material": "سوستة", "quantity": 1, "unit": "قطعة"},
        ],
    }

    return material_definitions.get(product.name, [])