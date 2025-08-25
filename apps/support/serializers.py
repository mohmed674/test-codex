from rest_framework import serializers
from .models import SupportTicket, SupportResponse

class SupportResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportResponse
        fields = '__all__'

class SupportTicketSerializer(serializers.ModelSerializer):
    responses = SupportResponseSerializer(many=True, read_only=True)

    class Meta:
        model = SupportTicket
        fields = '__all__'
