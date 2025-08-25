from rest_framework import serializers
from .models import POSOrder, POSOrderItem, POSSession

class POSOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSOrderItem
        fields = '__all__'

class POSOrderSerializer(serializers.ModelSerializer):
    items = POSOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = POSOrder
        fields = ['id', 'session', 'client', 'timestamp', 'total', 'paid', 'payment_method', 'is_refunded', 'items']

class POSSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSSession
        fields = '__all__'
