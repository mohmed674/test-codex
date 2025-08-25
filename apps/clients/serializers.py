# ERP_CORE/clients/serializers.py

from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'phone', 'email', 'address', 'client_code', 'account_number', 'created_at']
