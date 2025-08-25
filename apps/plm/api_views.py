from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import (
    PLMDocument,
    ProductTemplate,
    ProductVersion,
    LifecycleStage,
    ProductLifecycle,
    Bom,
    BomLine,
    ChangeRequest,
    ChangeRequestItem,
)
from .serializers import (
    PLMDocumentSerializer,
    ProductTemplateSerializer,
    ProductVersionSerializer,
    LifecycleStageSerializer,
    ProductLifecycleSerializer,
    BomSerializer,
    BomLineSerializer,
    ChangeRequestSerializer,
    ChangeRequestItemSerializer,
)


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ()
    ordering_fields = ()
    ordering = ("id",)


class PLMDocumentViewSet(BaseViewSet):
    queryset = PLMDocument.objects.all()
    serializer_class = PLMDocumentSerializer
    search_fields = ("name", "version")
    ordering_fields = ("id", "name", "version", "created_at")
    ordering = ("-created_at",)


class ProductTemplateViewSet(BaseViewSet):
    queryset = ProductTemplate.objects.all()
    serializer_class = ProductTemplateSerializer
    search_fields = ("code", "name", "category")
    ordering_fields = ("code", "name", "category", "uom", "active", "created_at")
    ordering = ("code",)


class ProductVersionViewSet(BaseViewSet):
    queryset = ProductVersion.objects.select_related("product").prefetch_related("documents").all()
    serializer_class = ProductVersionSerializer
    search_fields = ("version_code", "title", "product__code", "product__name", "status")
    ordering_fields = ("version_code", "status", "is_active", "effective_from", "effective_to", "created_at")
    ordering = ("product__code", "version_code")


class LifecycleStageViewSet(BaseViewSet):
    queryset = LifecycleStage.objects.all()
    serializer_class = LifecycleStageSerializer
    search_fields = ("name",)
    ordering_fields = ("order", "name", "id")
    ordering = ("order", "name")


class ProductLifecycleViewSet(BaseViewSet):
    queryset = ProductLifecycle.objects.select_related("product", "stage").all()
    serializer_class = ProductLifecycleSerializer
    search_fields = ("product__code", "product__name", "stage__name")
    ordering_fields = ("started_at", "ended_at", "id")
    ordering = ("-started_at",)


class BomViewSet(BaseViewSet):
    queryset = Bom.objects.select_related("product_version", "product_version__product").prefetch_related("lines").all()
    serializer_class = BomSerializer
    search_fields = ("code", "product_version__version_code", "product_version__product__code", "product_version__product__name")
    ordering_fields = ("code", "is_active", "created_at")
    ordering = ("product_version__product__code", "product_version__version_code", "code")


class BomLineViewSet(BaseViewSet):
    queryset = BomLine.objects.select_related("bom", "component").all()
    serializer_class = BomLineSerializer
    search_fields = ("bom__code", "component__code", "component__name", "description", "operation")
    ordering_fields = ("order", "quantity", "uom", "wastage_pct", "id")
    ordering = ("bom__code", "order", "id")


class ChangeRequestViewSet(BaseViewSet):
    queryset = ChangeRequest.objects.select_related("product", "from_version", "to_version").prefetch_related("attachments", "items").all()
    serializer_class = ChangeRequestSerializer
    search_fields = ("number", "product__code", "product__name", "status", "change_type", "reason", "requested_by", "approved_by")
    ordering_fields = ("created_at", "approved_at", "implemented_at", "status", "change_type", "number")
    ordering = ("-created_at", "number")


class ChangeRequestItemViewSet(BaseViewSet):
    queryset = ChangeRequestItem.objects.select_related("change_request", "bom", "bom_line").all()
    serializer_class = ChangeRequestItemSerializer
    search_fields = ("change_request__number", "bom__code", "bom_line__component__code", "bom_line__component__name")
    ordering_fields = ("id",)
    ordering = ("id",)
