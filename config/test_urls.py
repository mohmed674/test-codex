# config/test_urls.py — URLConf مخصّص للاختبارات فقط

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def ok_view(_request):
    """فحص سريع لصحة السيرفر أثناء الاختبارات."""
    return JsonResponse({"ok": True})


# نقاط نهاية مبسطة لتفادي استيراد مسارات غير متوفرة في بيئة الاختبار
employee_patterns = ([path("", ok_view, name="list")], "employees")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__ok__", ok_view),
    path("employees/", include(employee_patterns, namespace="employees")),
    path("employee-monitoring/", ok_view),
    path("survey/", ok_view),
    path("media/", ok_view),
]
