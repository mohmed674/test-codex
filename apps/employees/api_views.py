# ERP_CORE/employees/api_views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Employee, AttendanceRecord, MonthlyIncentive
from .serializers import (
    EmployeeSerializer,
    AttendanceRecordSerializer,
    MonthlyIncentiveSerializer,
)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['department', 'gender', 'active']
    search_fields = ['name', 'national_id', 'phone']

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'date', 'is_absent', 'is_excused_absence']

class MonthlyIncentiveViewSet(viewsets.ModelViewSet):
    queryset = MonthlyIncentive.objects.all()
    serializer_class = MonthlyIncentiveSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'month']
