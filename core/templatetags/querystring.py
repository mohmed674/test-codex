# core/templatetags/querystring.py
from typing import Any

from django import template
from django.http import HttpRequest
from django.utils.http import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def qs_replace(context: dict[str, Any], **kwargs: Any) -> str:
    """
    يبني QueryString جديد مع تبديل/حذف مفاتيح بدون تكرار page.
    الاستخدام:
        ?{% qs_replace page=3 %}
        ?{% qs_replace page=None %}  # لحذف المفتاح
    """
    request: HttpRequest = context["request"]
    query = request.GET.copy()

    for key, value in kwargs.items():
        if value is None:
            query.pop(key, None)
        else:
            query[key] = value

    return urlencode(query, doseq=True)
