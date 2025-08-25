# resilient suppliers api urls
from django.urls import path
from django.http import JsonResponse

# جرّب استيراد كلاسّات API إن وُجدت، وإلّا استخدم بدائل خفيفة
try:
    from apps.suppliers import api_views as _api
    HAVE_API_VIEWS = True
except Exception:
    HAVE_API_VIEWS = False

def _fallback_list(request):
    return JsonResponse({"ok": True, "endpoint": "suppliers/api/list", "using": "fallback"}, status=200)

def _fallback_detail(request, pk:int):
    return JsonResponse({"ok": True, "endpoint": f"suppliers/api/detail/{pk}", "using": "fallback"}, status=200)

urlpatterns = []

# لو فيه SupplierListAPIView/SupplierDetailAPIView نستخدمهم، غير كده البديل
if HAVE_API_VIEWS and hasattr(_api, "SupplierListAPIView"):
    urlpatterns.append(path("list/", _api.SupplierListAPIView.as_view(), name="supplier_list_api"))
else:
    urlpatterns.append(path("list/", _fallback_list, name="supplier_list_api"))

if HAVE_API_VIEWS and hasattr(_api, "SupplierDetailAPIView"):
    urlpatterns.append(path("detail/<int:pk>/", _api.SupplierDetailAPIView.as_view(), name="supplier_detail_api"))
else:
    urlpatterns.append(path("detail/<int:pk>/", _fallback_detail, name="supplier_detail_api"))
