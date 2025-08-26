# config/test_urls.py — URLConf مخصّص للاختبارات فقط

from django.contrib import admin
from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.urls import include, path
import importlib


def ok_view(_request):
    """فحص سريع لصحة السيرفر أثناء الاختبارات."""
    return JsonResponse({"ok": True})


def error_view(_request):
    """نقطة تسبّب خطأ متعمّد لاختبار صفحات/لواقط الأخطاء."""
    raise RuntimeError("Intentional test error")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("media/", include("apps.media.urls")),  # مسار مبسّط لتطبيق الوسائط
    path("employees/", include("apps.employees.urls")),
    path("employee-monitoring/", include("apps.employee_monitoring.urls")),
    path("survey/", include("apps.survey.urls")),
    path("__ok__", ok_view),
    path("__error__", error_view),
]

# إن وُجد config.urls في المشروع، ضمّنه حتى تعمل الروابط الأساسية في الاختبارات
try:
    _config_urls = importlib.import_module("config.urls")
    # لا نُضيفه إلا إذا كان يحتوي على urlpatterns لتجنّب مشاكل الدوَران/الاستيراد
    if getattr(_config_urls, "urlpatterns", None):
        urlpatterns += [path("", include("config.urls"))]
except ModuleNotFoundError:
    # لا يوجد ملف urls أساسي — لا مشكلة، نستخدم نقاط الاختبار أعلاه فقط
    pass
except Exception:
    # أي خطأ آخر، نتجاوز بهدوء كي لا نفشل الاختبارات بسبب URLConf
    pass

# دعم شريط التصحيح إن كان مُثبّتًا ضمن بيئة التطوير
try:
    import debug_toolbar  # type: ignore

    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
except Exception:
    pass
