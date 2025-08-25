# ERP_CORE/employees/api_views.py

from rest_framework import viewsets
from .models import Employee, AttendanceRecord, MonthlyIncentive
from .serializers import EmployeeSerializer, AttendanceRecordSerializer, MonthlyIncentiveSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filterset_fields = ['department', 'gender', 'active']
    search_fields = ['name', 'national_id', 'phone']

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    filterset_fields = ['employee', 'date', 'is_absent', 'is_excused_absence']

class MonthlyIncentiveViewSet(viewsets.ModelViewSet):
    queryset = MonthlyIncentive.objects.all()
    serializer_class = MonthlyIncentiveSerializer
    filterset_fields = ['employee', 'month']
