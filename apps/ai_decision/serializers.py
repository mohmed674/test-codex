# ERP_CORE/ai_decision/serializers.py

from rest_framework import serializers
from .models import AIDecisionAlert, AIDecisionLog

class AIDecisionAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIDecisionAlert
        fields = '__all__'

class AIDecisionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIDecisionLog
        fields = '__all__'
