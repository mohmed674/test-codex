# ERP_CORE/employees/serializers.py

from rest_framework import serializers
from .models import Employee, AttendanceRecord, MonthlyIncentive
from apps.departments.models import Department  # لو مستخدم في علاقات

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class EmployeeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department', write_only=True, required=False
    )

    class Meta:
        model = Employee
        fields = [
            'id', 'name', 'job_title', 'gender', 'department', 'department_id',
            'national_id', 'phone', 'hire_date', 'active',
            'total_rewards', 'total_deductions', 'total_warnings',
            'total_evaluations', 'evaluation_score', 'behavior_status'
        ]
        read_only_fields = ['total_rewards', 'total_deductions', 'total_warnings', 'total_evaluations', 'evaluation_score', 'behavior_status']

class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), source='employee', write_only=True
    )

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'employee', 'employee_id', 'date', 'check_in', 'is_absent', 'is_excused_absence']

class MonthlyIncentiveSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), source='employee', write_only=True
    )

    class Meta:
        model = MonthlyIncentive
        fields = ['id', 'employee', 'employee_id', 'month', 'commitment_bonus', 'quarterly_bonus', 'penalty_total']
