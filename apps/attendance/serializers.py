# ERP_CORE/attendance/serializers.py

from rest_framework import serializers
from .models import AttendanceRecord

class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'employee', 'employee_name', 'date', 'check_in', 'check_out', 'status', 'notes']
