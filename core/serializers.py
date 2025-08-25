# ERP_CORE/core/serializers.py

from rest_framework import serializers
from .models import (
    JobTitle, Unit, EvaluationCriteria,
    ProductionStageType, RiskThreshold, DepartmentRole
)

class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = '__all__'

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'

class EvaluationCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriteria
        fields = '__all__'

class ProductionStageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionStageType
        fields = '__all__'

class RiskThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskThreshold
        fields = '__all__'

class DepartmentRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentRole
        fields = '__all__'
