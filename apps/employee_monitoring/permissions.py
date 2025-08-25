# ERP_CORE/employee_monitoring/serializers.py

from rest_framework import serializers
from .models import MonitoringRecord, Evaluation

class MonitoringRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = MonitoringRecord
        fields = ['id', 'employee', 'employee_name', 'status', 'notes', 'date']


class EvaluationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = Evaluation
        fields = ['id', 'employee', 'employee_name', 'score', 'date']
