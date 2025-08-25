from rest_framework.routers import DefaultRouter
from .api_views import (
    PLMDocumentViewSet,
    ProductTemplateViewSet,
    ProductVersionViewSet,
    LifecycleStageViewSet,
    ProductLifecycleViewSet,
    BomViewSet,
    BomLineViewSet,
    ChangeRequestViewSet,
    ChangeRequestItemViewSet,
)

app_name = "plm_api"

router = DefaultRouter()
router.register(r"documents", PLMDocumentViewSet, basename="plm-document")
router.register(r"products", ProductTemplateViewSet, basename="plm-product")
router.register(r"versions", ProductVersionViewSet, basename="plm-version")
router.register(r"stages", LifecycleStageViewSet, basename="plm-stage")
router.register(r"lifecycles", ProductLifecycleViewSet, basename="plm-lifecycle")
router.register(r"boms", BomViewSet, basename="plm-bom")
router.register(r"bom-lines", BomLineViewSet, basename="plm-bomline")
router.register(r"change-requests", ChangeRequestViewSet, basename="plm-changerequest")
router.register(r"change-request-items", ChangeRequestItemViewSet, basename="plm-changerequestitem")

urlpatterns = router.urls
