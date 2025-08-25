from rest_framework import serializers
from .models import LegalCase

class LegalCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalCase
        fields = '__all__'
