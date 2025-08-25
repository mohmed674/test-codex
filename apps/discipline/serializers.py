# ERP_CORE/discipline/serializers.py

from rest_framework import serializers
from .models import DisciplineRecord

class DisciplineRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = DisciplineRecord
        fields = [
            'id',
            'employee', 'employee_name',
            'type', 'value_type', 'value',
            'reason', 'created_by', 'date',
            'related_month', 'is_approved', 'notes'
        ]
        read_only_fields = ['date', 'related_month']
