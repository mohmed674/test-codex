from rest_framework import serializers
from .models import Campaign, CampaignTarget

class CampaignTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignTarget
        fields = '__all__'

class CampaignSerializer(serializers.ModelSerializer):
    targets = CampaignTargetSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = '__all__'
