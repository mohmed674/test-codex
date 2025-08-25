from django import template
from core.utils import get_entry_hint

register = template.Library()

# ✅ فلتر لإضافة CSS class للحقل داخل القالب
@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

# ✅ فلتر للحصول على النص التوضيحي الذكي حسب الحقل والقسم
@register.filter(name='get_hint')
def get_hint(field_name, section):
    return get_entry_hint(field_name, section)

# ✅ فلتر للحصول على قيمة من dict باستخدام مفتاح
@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key, '')
