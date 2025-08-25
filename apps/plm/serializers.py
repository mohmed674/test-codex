from rest_framework import serializers
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


class PLMDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PLMDocument
        fields = "__all__"


class ProductTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTemplate
        fields = "__all__"


class ProductVersionSerializer(serializers.ModelSerializer):
    product = ProductTemplateSerializer(read_only=True)
    documents = PLMDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVersion
        fields = "__all__"


class LifecycleStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifecycleStage
        fields = "__all__"


class ProductLifecycleSerializer(serializers.ModelSerializer):
    product = ProductTemplateSerializer(read_only=True)
    stage = LifecycleStageSerializer(read_only=True)

    class Meta:
        model = ProductLifecycle
        fields = "__all__"


class BomLineSerializer(serializers.ModelSerializer):
    component = ProductTemplateSerializer(read_only=True)

    class Meta:
        model = BomLine
        fields = "__all__"


class BomSerializer(serializers.ModelSerializer):
    product_version = ProductVersionSerializer(read_only=True)
    lines = BomLineSerializer(many=True, read_only=True)

    class Meta:
        model = Bom
        fields = "__all__"


class ChangeRequestItemSerializer(serializers.ModelSerializer):
    bom = BomSerializer(read_only=True)
    bom_line = BomLineSerializer(read_only=True)

    class Meta:
        model = ChangeRequestItem
        fields = "__all__"


class ChangeRequestSerializer(serializers.ModelSerializer):
    product = ProductTemplateSerializer(read_only=True)
    from_version = ProductVersionSerializer(read_only=True)
    to_version = ProductVersionSerializer(read_only=True)
    attachments = PLMDocumentSerializer(many=True, read_only=True)
    items = ChangeRequestItemSerializer(many=True, read_only=True)

    class Meta:
        model = ChangeRequest
        fields = "__all__"

