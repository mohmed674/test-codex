# ضع الملف داخل core/templatetags/ (لو المجلد مش موجود اعمله مع __init__.py فارغ)
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def qs_replace(context, **kwargs):
    """
    يبني querystring جديد مع تبديل/حذف مفاتيح بدون تكرار ?page
    الاستخدام: ?{% qs_replace page=3 %}
               ?{% qs_replace page=None %}  # لحذف المفتاح
    """
    request = context['request']
    query = request.GET.copy()
    for k, v in kwargs.items():
        if v is None:
            query.pop(k, None)
        else:
            query[k] = v
    return query.urlencode()
