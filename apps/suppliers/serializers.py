# suppliers/serializers.py

from rest_framework import serializers
from apps.accounting.models import Supplier

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
