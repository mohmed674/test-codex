# ERP_CORE/purchases/serializers.py

from rest_framework import serializers
from .models import PurchaseRequest, PurchaseItem, PurchaseOrder, PurchaseInvoice


class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = ['product', 'quantity', 'notes']


class PurchaseRequestSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = ['id', 'requested_by', 'department', 'purpose', 'status', 'created_at', 'items']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'


class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInvoice
        fields = '__all__'
