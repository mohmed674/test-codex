from rest_framework.routers import DefaultRouter
from .api_views import SupplierViewSet

app_name = 'suppliers_api'

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')

urlpatterns = router.urls
